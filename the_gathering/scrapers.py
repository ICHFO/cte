import pymongo
import yaml
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

with open('config.yaml') as f:
	config = yaml.load(f)
	mongohost = config.get('mongo_host')
	mcon = pymongo.MongoClient(mongohost)
	mdb = mcon["cte"]
	vcol = mdb["vacancies"]
	scol = mdb["breaks"]


def Scraper(site):
	scraper_dict = {
		'vdab' : VdabScraper(site),
		'indeed': IndeedScraper(site)
	}
	return scraper_dict.get(site)

def _get_driver():
	options = Options()
	options.headless = True
	return webdriver.Firefox(options=options,executable_path='/usr/bin/gd')

class _Scraper():
	def __init__(self, site):
		self.site = site
		self.base_url = config.get(site)
		self.break_url = None
		self.links = list()
		self.driver = _get_driver()
		self.driver.implicitly_wait(1)

	def scrape_pages(self, init=False):
		if init:
			print("init - dropping collection")
			vcol.drop()
			self.extract_init()
		else:
			print("not init")
			self.extract_urls()
		for url in self.links:
			print(url)
			self.driver.get(url)
			vacancy = dict( site=self.site,
							url=url,
							source=self.driver.page_source)
			r = vcol.insert_one(vacancy)
			print(r)
		scol.update_one({"site": self.site},{'set': { 'break_url' : self.links[0]}})


class VdabScraper(_Scraper):
	def extract_urls(self):
		self.break_url = scol.find({'site' : self.site},{'break_url' : 1})
		for i in range(1,2):
			url = f"{self.base_url}{i}"
			self.driver.get(url)
			for e in self.driver.find_elements_by_class_name('display-block'):
				link = e.find_element_by_class_name('slat-link').get_attribute('href')
				if link == self.break_url:
					return
				self.links.append(link)

	def extract_init(self):
		scol.insert_one(dict(site=self.site,break_url=""))
		for i in range(1,201):
			url = f"{self.base_url}{i}"
			print(f"Scraping {url}")
			self.driver.get(url)
			for e in self.driver.find_elements_by_class_name('display-block'):
				link = e.find_element_by_class_name('slat-link').get_attribute('href')
				self.links.append(link)

class IndeedScraper(_Scraper):
	def extract_urls(self):
		return None
	

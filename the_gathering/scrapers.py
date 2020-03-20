import pymongo
import yaml
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException

with open('config.yaml') as f:
	config = yaml.load(f)
	gecko = config.get('gecko_bin')
	mongo = config.get('mongo_host')
	mcon = pymongo.MongoClient(mongo)
	mdb = mcon["cte"]
	vcol = mdb["vacancies"]
	scol = mdb["sites"]


def Scraper(site):
	scraper_dict = {
		'vdab' : VdabScraper,
		'indeed': IndeedScraper
	}
	return scraper_dict.get(site)(site)

# BASE SCRAPER
##############

def _get_driver():
	options = Options()
	options.headless = True
	return webdriver.Firefox(options=options,executable_path=gecko)

class _Scraper():
	def __init__(self, site):
		print(f"{datetime.now()} : initializing {site} scraper")
		self.site = site
		s = scol.find({"site":self.site})[0]
		self.base_url = s.get('base_url')
		self.break_url = s.get('break_url')
		self.links = list()
		self.driver = _get_driver()
		self.driver.implicitly_wait(1)
		self.ex_count = 0

	def __del__(self):
		if self.driver:
			self.driver.close()

	def scrape_pages(self):
		self.extract_urls()
		print(f"{datetime.now()} : Scraping {len(self.links)} pages")
		for url in self.links:
			try:
				self.driver.get(url)
			except TimeoutException:
				print(f"{datetime.now()} : timeout occured")
				self.ex_count += 1
			vacancy = dict( site=self.site,
							scrape_date=str(datetime.date(datetime.now())),
							url=url,
							source=self.driver.page_source)
			r = vcol.insert_one(vacancy)
		if len(self.links) > 0:
			scol.update_one({"site": self.site},{'$set': { 'break_url' : self.links[0]}})
			print(f"{datetime.now()} : {len(self.links) - self.ex_count} new pages added")
		else:
			print(f"{datetime.now()} : No new pages added.")

# SITE SPECIFIC SCRAPER IMPLEMENTAIONS
######################################

class VdabScraper(_Scraper):
	def extract_urls(self):
		print(f"{datetime.now()} : collecting links.")
		for i in range(1,201):
			url = f"{self.base_url}{i}"
			self.driver.get(url)
			for w in self.driver.window_handles:
				self.driver.switch_to_window(w)
				for e in self.driver.find_elements_by_class_name('display-block'):
					link = e.find_element_by_class_name('slat-link').get_attribute('href')
					if link == self.break_url:
						return
					self.links.append(link)


class IndeedScraper(_Scraper):
	def extract_urls(self):
		print(f"{datetime.now()} : collecting links.")
		for i in range(0,991,10):
			url = f"{self.base_url}{i}"
			self.driver.get(url)
			for w in self.driver.window_handles:
				self.driver.switch_to_window(w)
				jobcards = self.driver.find_elements_by_class_name('jobsearch-SerpJobCard')
				for j in jobcards:
					title = j.find_element_by_class_name('title')
					link = title.find_element_by_tag_name('a').get_attribute('href')
					if link == self.break_url:
						return
					self.links.append(link)

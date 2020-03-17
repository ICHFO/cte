import pymongo
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

def Scraper(site):
         return scraper_dict.get(site)

def _get_driver():
        options = Options()
        options.headless = True
        return webdriver.Firefox(options=options,executable_path='/usr/bin/gd')

class _Scraper():
        def __init__(self, base_url):
                self.base_url = base_url
                self.break_url = None
                self.links = list()
                self.driver = _get_driver()
                self.driver.implicitly_wait(1)

        def scrape_pages(self, init=False):
                mcon = pymongo.MongoClient("mongodb://localhost:27017/")
                mdb = mcon["cte"]
                mcol = mdb["vacancies"]
                if init:
                        print("init - dropping collection")
                        mcol.drop()
                        self.extract_init()
                else:
                        print("not init")
                        self.extract_urls()
                for url in self.links:
                        self.driver.get(url)
                        vacancy = dict(site=url.split('//')[1].split('.')[1],
                                                                                 url= url,
                                                                                 source=self.driver.page_source)
                        mcol.insert_one(vacancy)
                self.break_url = self.links[0]



class VdabScraper(_Scraper):
        def extract_urls(self):
                for i in range(1,4):
                        url = f"{self.base_url}{i}"
                        self.driver.get(url)
                        for e in self.driver.find_elements_by_class_name('display-block'):
                                link = e.find_element_by_class_name('slat-link').get_attribute('href')
                                if link == self.break_url:
                                        return
                                self.links.append(link)

        def extract_init(self):
                self.driver.implicitly_wait(1)
                for i in range(1,201):
                        url = f"{self.base_url}{i}"
                        self.driver.get(url)
                        for e in self.driver.find_elements_by_class_name('display-block'):
                                link = e.find_element_by_class_name('slat-link').get_attribute('href')
                                self.links.append(link)

class IndeedScraper(_Scraper):
        def extract_urls(self):
                return None

scraper_dict = {
  'vdab' : VdabScraper,
  'indeed': IndeedScraper
}

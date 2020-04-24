import ibm_db
import pymongo
import yaml
import logging
from pymongo.errors import DuplicateKeyError, WriteError
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException


with open('/home/ic/cte/the_harvest/config.yaml') as f:
    cfg = yaml.load(f)
    gecko_bin = cfg.get('gecko_bin')
    gecko_log = f"{cfg.get('gecko_log')}/geckodriver.log"
    mongo = cfg.get('mongo_host')
    mcon = pymongo.MongoClient(mongo)
    mdb = mcon["cte"]
    vcol = mdb["vacancies"]
    scol = mdb["sites"]
    logname = f"{datetime.date(datetime.now())}_harvest.log"
    logging.basicConfig(filename=f"{cfg.get('log_path')}/{logname}",
                        level=cfg.get('log_level'),
                        format=cfg.get('log_format'),
                        datefmt=cfg.get('log_date_format'))


def Harvester(site):
    scraper_dict = {
        'amon': AmonHarvester,
        'careerjet': CareerjetHarvester,
        'indeed': IndeedHarvester,
        'jobat': JobatHarvester,
        'vdab': VdabHarvester
    }
    return scraper_dict.get(site)(site)


# BASE SCRAPER
##############

def _get_driver():
    options = Options()
    options.headless = True
    return webdriver.Firefox(options=options, executable_path=gecko_bin, service_log_path=gecko_log)


class _Harvester():
    def __init__(self, site):
        logging.info(f"initializing {site} scraper")
        self.site = site
        s = scol.find({"site": self.site})[0]
        self.base_url = s.get('base_url')
        self.break_url = s.get('break_url')
        self.links = list()
        self.driver = _get_driver()
        self.driver.implicitly_wait(1)
        self.ex_count = 0

        db2_cstr = "DATABASE=cte;HOSTNAME=skye.infocura.lan;PORT=50001;PROTOCOL=TCPIP;UID=ic;PWD=icmaster"
        self.db2_conn = ibm_db.connect(db2_cstr, '', '')

    def __del__(self):
        if self.driver:
            self.driver.close()
        if self.db2_conn:
            ibm_db.close(self.db2_conn)

    def scrape_pages(self):
        self.extract_urls()
        logging.info(f"scraping {len(self.links)} pages")
        for url in self.links:
            try:
                self.driver.get(url)
                vac = {
                    'site'		: self.site,
                    'scrape_dat'	: str(datetime.date(datetime.now())),
                    'url'			: url,
                    'source'		: self.driver.page_source
                }
                vcol.insert_one(vac)
            except TimeoutException:
                logging.error(f"timeout occured")
                self.ex_count += 1
            except DuplicateKeyError:
                pass
            except WriteError as e:
                logging.error(e)

        if len(self.links) > 0:
            scol.update_one({"site": self.site },{'$set':{ 'break_ur' : self.links[0]}})
            logging.info(f"{len(self.links) - self.ex_count} new pages added")
            self.add_db2_record(url, self.driver.page_source)
        else:
            logging.info("no new pages added")

    def rescrape_page(self, url):
        try:
            self.driver.get(url)
        except TimeoutException:
            logging.warning("timeout occured")
        finally:
            vcol.find_one_and_update({'url ':url},
                                     {'$set': {'source': self.driver.page_source}})
            self.add_db2_record(url, self.driver.page_source)

    def add_db2_record(self, url: str, html: str):
        sql = f"insert into cte.vancany_raw (url, html) values ('{url}', '{html}')"
        try:
            stmt = ibm_db.exec_immediate(self.db2_conn, sql)
        except:
            logging.info(f"insert failed for {url}")



########################################
# SITE SPECIFIC SCRAPER IMPLEMENTAIONS #
########################################

class AmonHarvester(_Harvester):
    def extract_urls(self):
        for i in range( 0,14):
            url = f"{self.base_url}{i}"
            self.driver.get(url)
            for  w in self.driver.window_handles:
                self.driver.switch_to_window(w)
                for e in self.driver.find_elements_by_class_name('vacancy'):
                    link = e.get_attribute('href')
                    if link == self.break_url:
                        return
                    self.links.append(link)


class CareerjetHarvester(_Harvester):
    def extract_urls(self):
        for i in range( 0,199,2):
            url = f"{self.base_url}{i}1&sort=date&cid=52"
            self.driver.get(url)
            for w in self.driver.window_handles:
                self.driver.switch_to_window(w)
                for e in self.driver.find_elements_by_class_name('job'):
                    link = e.find_element_by_tag_name('a').get_attribute('href')
                    if link == self.break_url:
                        return
                    self.links.append(link)


class VdabHarvester(_Harvester):
    def extract_urls(self):
        for i in range( 1,201):
            url = f"{self.base_url}{i}"
            self.driver.get(url)
            for w in self.driver.window_handles:
                self.driver.switch_to_window(w)
                for e in self.driver.find_elements_by_class_name('display-block'):
                    link = e.find_element_by_class_name('slat-link').get_attribute('href')
                    if link == self.break_url:
                        return
                    self.links.append(link)


class IndeedHarvester(_Harvester):
    def extract_urls(self):
        for i in range( 0,991,10):
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


class JobatHarvester(_Harvester):
    def extract_urls(self):
        for i in range( 1,4):
            url = f"{self.base_url}{i}"
            self.driver.get(url)
            for w in self.driver.window_handles:
                self.driver.switch_to_window(w)
                for e in self.driver.find_elements_by_class_name('jobCard-title'):
                    link = e.find_element_by_tag_name('a').get_attribute('href')
                    if link == self.break_url:
                        return
                    self.links.append(link)

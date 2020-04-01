The Purge:
Maakt van een document een verfijnder document en slaagt dat op in mongo

vacancies collect:
{
    site : string -> 'vdab'/'indeed'/'jobat'/....
    scrape_date : date 
    url : string
    source : string -> volledige html pagina als string
}

vac_p collection:
{
    site : string
    url : string
    company : string
    title : string
    location : string
    date : date -> date vacancy was put online
    description : string
    skills : string
    offer : string
}import pymongo, traceback, sys
from pymongo.errors import BulkWriteError
from bs4 import BeautifulSoup
from datetime import datetime
from config import Config as cfg
from setup import get_mongo_client, get_es_client


def Purger(site):
    purger_dict = {
        'amon'	: None,
        'careerjet'	: None,
        'indeed'	: None,
        'jobat'		: None,
        'vdab'		: VdabPurger,
    }
    if purger_dict.get(site):
        return purger_dict.get(site)(site)


class _Purger():
    def __init__(self, site):
        self.site = site
        self.db = get_mongo_client()['cte']
        self.es = get_es_client()

    def run(self):
        self.db.vac_p.drop()
        doc_lst = list()
        print("purging documents")
        prev_url = ''
        for doc in self.db['vacancies'].find({'site' : self.site}):
            soup = BeautifulSoup(doc.get('source') ,'html.parser')
            try:
                p_doc = {
                    'site' : doc.get('site'),
                    'url'  : doc.get('url'),
                    'company' : self.get_company(soup),
                    'title' : self.get_title(soup),
                    'location' : self.get_location(soup),
                    'date' : self.get_date(soup),
                    'description' : self.get_description(soup),
                    'skills' : self.get_skills(soup),
                    'offer'	: self.get_offer(soup)
                }
                doc_lst.append(p_doc)
            except Exception:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_tb(exc_traceback)
                print(f"{exc_value} - {prev_url}")
            prev_url = doc.get('url')
        print("inserting documents")
        self.db.vac_p.insert_many(doc_lst)

    def get_title(self ,soup):
        return "unknown"

    def get_company(self ,soup):
        return "unkown"

    def get_zip(eself ,soup):
        return "unknown"

    def get_location(self ,soup):
        return "unknown"

    def get_date(self ,soup):
        return "unknown"

    def get_description(self ,soup):
        return "unknown"

    def get_skills(self ,soup):
        return "unknown"

    def get_offer(self ,soup):
        return "unkown"


class VdabPurger(_Purger):
    def get_title(self ,soup):
        title = soup.find('h1', id='vej-vacature-detail-title').get_text()
        return title.replace('\n', '').lstrip().rstrip()

    def get_company(self, soup):
        t1 = soup.find_all('p', class_='mb0')[0]
        company = t1.find_all('strong')[0].get_text()
        return company.lower()

    def get_zip(self, soup):
        tag = soup.find('span' ,itemprop='postalCode')
        if tag:
            return tag.get_text(strip=True)
        return "unknown"

    def get_location(self, soup):
        tag = soup.find('span', itemprop='addressLocality')
        if tag:
            return tag.get_text(strip=True).lower()
        return soup.find('span', itemprop='address').get_text(strip=True).lower()

    def get_date(self, soup):
        mmap = {'jan.' :1, 'feb.' :2, 'mrt.' :3, 'apr.' :4, 'mei' :5, 'jun.' :6, 'jul.' :7,
                'aug.' :9, 'sep.' :9, 'okt.' :10, 'nov.' :11, 'dec.' :12 }
        dlst = soup.find_all('p', class_='mb0')[1].span.get_text(strip=True).split(' ')
        dt_online = datetime.strptime(f"{dlst[4]}-{mmap.get(dlst[3])}-{dlst[2]}", '%Y-%m-%d')
        return dt_online

    def get_description(self, soup):
        text = soup.find('span' ,itemprop='description').get_text()
        text += soup.find('p', class_='mb1' ,itemprop='skills').get_text()
        tag = soup.find('ul' ,class_='competenties')
        if tag : text += tag.get_text()
        return text

	def get_skills(self,soup):
		

if __name__ == '__main__':
    p = Purger('vdab')
    if p:
        p.run()

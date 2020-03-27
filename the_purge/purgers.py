import pymongo, traceback, sys
from pymongo.errors import BulkWriteError
from bs4 import BeautifulSoup
from datetime import datetime

def Purger(site):
	purger_dict = {
		'amon'		: None,
		'careerjet'	: None,
		'indeed'	: None,
		'jobat'		: None,
		'vdab'		: VdabPurger,
	}
	if purger_dict.get(site):
		return purger_dict.get(site)(site)
	else:
		print('Not implemented')
		exit(1)

def _get_db():
	return pymongo.MongoClient('penny.infocura.lan')['cte']


class _Purger():
	def __init__(self, site):
		self.site = site
		self.db = _get_db()	

	def run(self):
		self.db.vac_p.drop()
		doc_lst = list()
		print("purging documents")
		prev_url = ''
		for doc in self.db['vacancies'].find({'site' : self.site}):
			soup = BeautifulSoup(doc.get('source'),'html.parser')
			try:
				p_doc = {
					'site' : doc.get('site'),
					'url'  : doc.get('url'),
					'company' : self.get_company(soup),
					'location' : self.get_location(soup),
					'date_online' : self.get_date_online(soup),
					'description' : self.get_description(soup)
				}
				doc_lst.append(p_doc)
			except Exception:
				exc_type, exc_value, exc_traceback = sys.exc_info()
				traceback.print_tb(exc_traceback)
				print(f"{exc_value} - {prev_url}")
			prev_url = doc.get('url')
		print("inserting documents")
		self.db.vac_p.insert_many(doc_lst)


class VdabPurger(_Purger):
	def get_company(self, soup):
		t1 = soup.find_all('p', class_='mb0')[0]
		company = t1.find_all('strong')[0].get_text()
		return company.lower()
	
	def get_post_code(self, soup):
		tag = soup.find('span',itemprop='postalCode')
		if tag:
			return tag.get_text(strip=True)
		return "unknown"	

	def get_location(self, soup):
		tag = soup.find('span',itemprop='addressLocality')
		if tag:
			return tag.get_text(strip=True).lower()
		return soup.find('span',itemprop='address').get_text(strip=True).lower()

	def get_date_online(self, soup):
		mmap = {'jan.':1, 'feb.':2, 'mrt.':3, 'apr.':4, 'mei':5, 'jun.':6, 'jul.':7,
				'aug.':9, 'sep.':9, 'okt.':10, 'nov.':11, 'dec.':12 }
		dlst = soup.find_all('p', class_='mb0')[1].span.get_text(strip=True).split(' ')
		dt_online = datetime.strptime(f"{dlst[4]}-{mmap.get(dlst[3])}-{dlst[2]}", '%Y-%m-%d')
		return dt_online

	def get_description(self, soup):
		text = soup.find('span',itemprop='description').get_text()
		text += soup.find('p', class_='mb1',itemprop='skills').get_text()
		tag = soup.find('ul',class_='competenties')
		if tag : text += tag.get_text()
		return text

if __name__ == '__main__':
	p = Purger('vdab')
	p.run()

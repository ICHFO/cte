import ibm_db
from config import Config as cfg
from pymongo import MongoClient
from elasticsearch import Elasticsearch

def get_db2_con():
	cstr = f"DATABASE={cfg.db2_db};HOSTNAME={cfg.db2_host};PORT={cfg.db2_port};PROTOCOL=TCPIP;UID={cfg.db2_user};PWD={cfg.db2_pass}"
	db2c = ibm_db.connect(cstr,'','')
	return db2c

def get_mongo_client():
	return MongoClient(cfg.mongo_host)


def get_es_client():
	es = Elasticsearch([{"host":"dasha.infocura.lan"}])
	return es

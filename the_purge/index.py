from elasticsearch import Elasticsearch
from pymongo import MongoClient

es = Elasticsearch([{"host":"dasha.infocura.lan","port":"9200"}])
mongo = MongoClient("penny.infocura.lan")
mcur = mongo.cte.vac_p.find()
for doc in mcur:
	print(doc)
	es_doc = {
		'company' : doc.get('company'),
		'location' : doc.get('location'),
		'description' : doc.get('description')
	}
	res = es.index(index='v_test',doc_type='vac',id=doc.get('_id'),body=es_doc)
	print(res)

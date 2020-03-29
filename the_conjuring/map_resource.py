import ibm_db
from bson.objectid import ObjectId
from pymongo import MongoClient
from config import Config as cfg
from setup import get_db2_con, get_mongo_client, get_es_client


def get_resource(conn, res_id):
	sql = "select * from cte.resources where f_name = 'hans'"
	cur = ibm_db.exec_immediate(conn, sql)
	row = ibm_db.fetch_assoc(cur)
	if row:
		print('ok')

def get_resource_skills(conn, res_id):
	skills = []
	sql = f"select name from cte.skills s, cte.resources r, cte.skillsmap sm where s.id = sm.s_id and sm.r_id = r.id and r.f_name = '{res_id}'"
	cur = ibm_db.exec_immediate(conn, sql)
	row = ibm_db.fetch_assoc(cur)
	while row:
		skills.append(row.get('NAME'))
		row = ibm_db.fetch_assoc(cur)
	return skills


def map():
	pass

if __name__ == '__main__':
	db2c = get_db2_con()
	es = get_es_client()
	mongo = get_mongo_client()
	skills = get_resource_skills(db2c, 'hans')
	search_params = {
		'match' : {
			'description' : skills[2]	
		}
	}
	res = es.search(index='v_test',body={"_source" : [1] , "query" : search_params},size=500)
	hits = res.get('hits').get('hits')
	ids = [ ObjectId(hit.get('_id')) for hit in hits ]
	cur = mongo.cte.vac_p.find({"_id" : { "$in" : ids}},{"url":1})
	for e in cur:
		print(e.get('url'))
	ibm_db.close(db2c)
	print(res)

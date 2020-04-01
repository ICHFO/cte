import ibm_db
from bson.objectid import ObjectId
from pymongo import MongoClient
from config import Config as cfg
from setup import get_db2_con, get_mongo_client, get_es_client
from datetime import datetime

def get_resource_id(conn, name):
	sql = f"select id from cte.resources where f_name = '{name}'"
	cur = ibm_db.exec_immediate(conn, sql)
	row = ibm_db.fetch_assoc(cur)
	print(row)
	if row:
		print('r')
		return row.get('ID')

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
	r_id = get_resource_id(db2c, 'hans')
	skills = get_resource_skills(db2c, 'hans')
	search_params = {
		'match' : {
			'description' : skills[2]	
		}
	}
	res = es.search(index='v_test',body={"_source" : ["url","date"] , "query" : search_params},size=20)

	hits = res.get('hits').get('hits')
	for hit in hits:
		url = hit.get('_source').get('url')
		print(hit.get('_source').get('date'))
		date = hit.get('_source').get('date')[:10]
		stmt = f"insert into cte.top_20 (r_id,url,date) values ({r_id},'{url}','{date}')"
		print(stmt)
		ibm_db.exec_immediate(db2c,stmt)	
	ibm_db.close(db2c)

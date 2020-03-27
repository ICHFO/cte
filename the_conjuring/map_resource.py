import ibm_db
from pymongo import MongoClient
from config import Config as cfg
from setup import get_db2_con, get_mongo_client


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
	get_resource_skills(db2c, 'hans')
	ibm_db.close(db2c)

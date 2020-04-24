import ibm_db
from pymongo import MongoClient


mongo = MongoClient('penny.infocura.lan')
db2cstr = "DATABASE=cte;HOSTNAME=skye.infocura.lan;PORT=50001;PROTOCOL=TCPIP;UID=ic;PWD=icmaster"
db2conn = ibm_db.connect(db2cstr, '', '')

mcur = mongo.cte.vacancies.find()
for item in mcur:
    url = item.get("url")
    html = item.get("source")
    sql = "insert into cte.vacancy_raw (site, url, html) values (?, ?, ?)"
    site = item.get("site")
    stmt = ibm_db.prepare(db2conn, sql)
    try:
        param = site, url, html
        ibm_db.execute(stmt, param)
    except:
        print("Transaction couldn't be completed:", ibm_db.stmt_errormsg())

ibm_db.close(db2conn)
mongo.close()
import sqlalchemy
from sqlalchemy import *
import ibm_db_sa

db2 = sqlalchemy.create_engine('ibm_db_sa://ic:icmaster@dasha.infocura.lan:50000/CTE')
metadata = MetaData()
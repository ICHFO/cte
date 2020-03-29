class Config:
        db2_host = "dasha.infocura.lan"
        db2_user = "ic"
        db2_pass = "icmaster"
        db2_port = "50000"
        db2_db   = "cte"

        mongo_host = "penny.infocura.lan"

        elastic_host = "dasha.infocura.lan"

		gecko_bin = "/usr/bin/gd"
		gecko_log = "/var/log/the_harvest/"

		log_path = "/var/log/cte/the_harvest/"
		log_level = "INFO"
		log_fmt = "%(asctime)s - %(levelname)s: %(message)s"
		log_date_fmt = "%H:%M:%S"


def get_db2c():
    cstr = f"DATABASE={cfg.db2_db};HOSTNAME={cfg.db2_host};PORT={cfg.db2_port};PROTOCOL=TCPIP;UID={cfg.db2_user};PWD={cfg.db2_pass}"
    db2c = ibm_db.connect(cstr,'','')
    return db2c

def get_mongo():
    return MongoClient(cfg.mongo_host)


def get_elastic():
    es = Elasticsearch([{"host":"dasha.infocura.lan"}])
    return es

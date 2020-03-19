import yaml, pymongo

with open('config.yaml') as f:
	config = yaml.load(f)

mcon = pymongo.MongoClient(config.get('mongo_host'))
mdb = mcon["cte"]
mcol = mdb["vacancies"]


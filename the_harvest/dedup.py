#!/usr/bin/python3
import pymongo

# Requires the PyMongo package.
# https://api.mongodb.com/python/current

client = pymongo.MongoClient('mongodb://penny.infocura.lan:27017/?readPreference=primary&appname=MongoDB%20Compass&ssl=false')
result = client['cte']['vacancies'].aggregate([
    {
        '$addFields': {
            'n': {
                '$sum': 1
            }
        }
    }, {
        '$group': {
            '_id': '$url', 
            'ids': {
                '$addToSet': '$_id'
            }, 
            'n': {
                '$sum': '$n'
            }
        }
    }, {
        '$match': {
            'n': {
                '$gt': 1
            }
        }
    }
])

print(len(list(result)))

exit(0)

for e in result:
	ids = e.get('ids')
	for i in ids[1:]:
		q = {'_id' : i }
		client['cte']['vacancies'].delete_one(q)



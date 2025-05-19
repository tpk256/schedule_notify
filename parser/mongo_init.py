from pymongo import MongoClient
from pymongo.synchronous.collection import Collection
client = MongoClient("localhost", 27017)

db = client['schedule']
collection_tables: Collection = db.course_form
print(type(collection_tables))
for c_f in (11, 12, 13, 14):
    if not collection_tables.find_one(c_f):
        collection_tables.insert_one({
            '_id': c_f,
            'tables': []
        })

print(db.list_collection_names())
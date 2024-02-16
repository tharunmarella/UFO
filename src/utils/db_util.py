import pymongo as pym


def db_init():
    global earnings_collection
    client = pym.MongoClient("mongodb://localhost:27017")
    db = client.local
    earnings_collection = db["earningsTest"]


def insert_many(resultList):
    earnings_collection.insert_many(resultList)

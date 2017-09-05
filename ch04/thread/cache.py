# -*- coding:utf-8 -*-
from datetime import datetime, timedelta

import pymongo


class MongoCache(object):
    def __init__(self, db, collection, client=None, expires=timedelta(days=30)):
        self.client = client \
                      or pymongo.MongoClient(host="localhost", port=27017)
        self.db = self.client[db]
        self.collection = self.db[collection]
        self.collection.create_index('timestamp',
                                     expireAfterSeconds=expires.total_seconds())

    def __getitem__(self, url):
        document = self.collection.find_one({"_id": url})
        if document:
            return document["result"]
        else:
            raise KeyError(url + "don't exist")

    def __setitem__(self, url, result):
        result = {'result': result, 'timestamp': datetime.utcnow()}
        self.collection.update({'_id': url}, {'$set': result}, upsert=True)

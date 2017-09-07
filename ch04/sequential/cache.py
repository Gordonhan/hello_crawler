# -*- coding:utf-8 -*-
from datetime import datetime, timedelta

import pymongo

DEFAULT_DB = 'topsite'
DEFAULT_COllECTION = 'top1t'


class MongoCache(object):
    def __init__(self, client=None, expires=timedelta(days=30)):
        self.client = client \
                      or pymongo.MongoClient(host="localhost", port=27017)
        self.db = self.client[DEFAULT_DB]
        self.collection = self.db[DEFAULT_COllECTION]
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

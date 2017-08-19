# -*- coding:utf-8 -*-

from pymongo import MongoClient, errors
from datetime import datetime, timedelta


class MongoQueue(object):
    OUTSTANDING, PROCESSING, COMPLETE = range(3)

    def __init__(self, db, collection, cline=None, timeout=300):
        self.cline = cline if cline\
            else MongoClient(host='localhost', port=27017)
        self.db = cline[db]
        self.collection = self.db[collection]
        self.timeout = timeout

    def __nonzero__(self):
        """如果还有url需要爬取，返回True"""
        record = self.collection.find_one(
            {'status': {'$ne': self.COMPLETE}}
        )
        return True if record else False

    def push(self, url):
        """将新的url增加到队列中，如果队列中还没有该url"""
        try:
            self.collection.insert({'_id': url, 'status': self.OUTSTANDING})
        except errors.DuplicateKeyError as e:
            # 该url已经在队列中
            pass

    def pop(self):
        """返回一个待爬取url，并将其状态设置为处理中。
        如果队列为空，抛出KeyError
        """
        record = self.collection.find_and_modify(
            query={'status': self.OUTSTANDING},
            update={'$set': {'status': self.PROCESSING,
                             'timestamp': datetime.now()}}
        )
        if record:
            return record['_id']
        else:
            self.repair()
            raise KeyError

    def complete(self, url):
        self.collection.update({'_id': url},
                               {'$set': {'status': self.COMPLETE}})

    def repair(self):
        """Release stalled jobs
        """
        record = self.collection.find_and_modify(
            query={
                'timestamp': {
                    '$lt': datetime.now() - timedelta(seconds=self.timeout)
                },
                'status': {'$ne': self.COMPLETE}
            },
            update={'$set': {'status': self.OUTSTANDING}}
        )
        if record:
            print 'Released:', record['_id']

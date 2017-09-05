# -*- coding:utf-8 -*-
"""
从抓取中文网站排行榜，保存到topsite.csv
"""
import csv


class ScrapingCallback(object):
    def __init__(self, max_urls=1000):
        self.max_urls = max_urls
        self.seed_url = 'http://s3.amazonaws.com/alexa-static/top-1m.csv.zip'

    def __call__(self, url, html):
        if url == self.seed_url:
            urls = []
            with csv.reader(open('topsite.csv', 'rb')) as r:
                r.next()
                for _, website in r:
                    urls.append(website)
                    if len(urls) == self.max_urls:
                        break
            return urls
        else:
            return []


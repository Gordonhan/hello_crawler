# -*- coding:utf-8 -*-
import csv


class ScrapingCallback(object):
    def __init__(self, max_urls=1000):
        self.max_urls = max_urls
        self.seed_url = 'http://example.webscraping.com'

    def __call__(self, url, html):
        if url == self.seed_url:
            urls = []
            with open('topsite.csv', 'rb') as f:
                r = csv.reader(f)
                r.next()
                for _, website in r:
                    urls.append(website)
                    if len(urls) == self.max_urls:
                        break
            urls.reverse()
            return urls
        else:
            return []

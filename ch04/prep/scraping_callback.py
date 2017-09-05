# -*- coding:utf-8 -*-
"""
从抓取中文网站排行榜，保存到topsite.csv
"""
import re
import lxml.html
import csv


class ScrapingCallback(object):
    def __init__(self):
        self.urls = 1
        self.writer = csv.writer(open('topsite.csv', 'wb'))
        self.fields = ('ranking', 'site')
        self.writer.writerow(self.fields)

    def __call__(self, url, html):
        # 抓取数据
        tree = lxml.html.fromstring(html)
        a = tree.cssselect('div.w320 > a')
        for _a in a:
            href = _a.get("href")
            href = href[href.rfind("_") + 1: href.rfind(".")]
            self.writer.writerow((self.urls, 'http://'+href))
            self.urls += 1


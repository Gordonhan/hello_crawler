# -*- coding:utf-8 -*-
"""
模块将从页面抓取的数据存储起来
"""
import re
import lxml.html
import csv


class ScrapingCallback(object):
    def __init__(self):
        self.writer = csv.writer(open('datas.csv', 'wb'))
        self.fields = ('area', 'population', 'iso', 'country', 'capital',
                       'continent', 'tld', 'currency_code', 'currency_name',
                       'phone', 'postal_code_format', 'postal_code_regex',
                       'languages', 'neighbours')
        self.writer.writerow(self.fields)

    def __call__(self, url, html):
        """抓取数据的函数"""
        if re.search("/view/", url):
            # 抓取数据
            tree = lxml.html.fromstring(html)
            datas = [tree.cssselect("tr#places_{0}__row > td.w2p_fw"
                                    .format(field))[0].text_content()
                     for field in self.fields]
            # 缓存数据
            self.writer.writerow(datas)

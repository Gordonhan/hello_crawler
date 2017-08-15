# -*- coding:utf-8 -*-
"""
模块定义了从页面抓取数据的函数
"""
import re
import lxml.html

FIELDS = ('area', 'population', 'iso', 'country', 'capital', 'continent', 'tld',
          'currency_code', 'currency_name', 'phone', 'postal_code_format',
          'postal_code_regex', 'languages', 'neighbours')


def scraping_callback(url, html):
    """抓取数据的函数"""
    if re.search("/view/", url):
        tree = lxml.html.fromstring(html)
        datas = [tree.cssselect("tr#places_{0}__row > td.w2p_fw"
                                .format(field))[0].text_content()
                 for field in FIELDS]
        print url, datas


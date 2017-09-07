# -*- coding:utf-8 -*-
"""
@author: Gordon Han
@contact: Gordon-Han@hotmail.com
"""
import string
import json

from downloader import Downloader
from cache import MongoCache


def search1():
    template_url = 'http://example.webscraping.com/places/ajax/search.json?' \
                   '&search_term={}&page_size=20&page={}'
    countries = set()

    d = Downloader(cache=MongoCache())
    for letter in string.lowercase:
        page = 0
        while True:
            html = d(template_url.format(letter, page))
            try:
                ajax = json.loads(html)
            except ValueError:
                # 返回已不是JSON
                ajax = None
            else:
                for record in ajax['records']:
                    # pretty_link = record['pretty_link']
                    country = record['country']
                    # id = record['id']
                    countries.add(country)
            page += 1
            if ajax is None or page > ajax['num_pages']:
                # 已到达尾页
                break
    with open('countries.txt', 'wb') as f:
        f.write('\r\n'.join(sorted(countries)))


# 利用边界一次获取全部
def search2():
    template_url = 'http://example.webscraping.com/places/ajax/search.json?' \
                   '&search_term={}&page_size={}&page={}'
    countries = set()
    d = Downloader(cache=MongoCache())

    html = d(template_url.format('.', 1000, 0))
    ajax = json.loads(html)
    for record in ajax['records']:
        countries.add(record['country'])

    with open('countries.txt', 'wb') as f:
        f.write('\r\n'.join(sorted(countries)))


search = search2


def main():
    search()


if __name__ == '__main__':
    main()

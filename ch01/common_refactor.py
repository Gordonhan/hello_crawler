# -*- coding:utf-8 -*-
"""
refactor common.py with Requests(http://cn.python-requests.org/zh_CN/latest/)
"""

import requests


def download1(url):
    return requests.get(url).text


def download2(url, user_agent='wswp', headers=None, proxies=None, timeout=5,
              debug=False):
    print 'Downloading:', url
    headers = headers or {}
    headers['user-agent'] = user_agent

    r = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)

    if debug:
        print r.request.headers
        print r.headers

    if r.status_code == 200:
        return r.text
    else:
        print "Download failed"
        r.raise_for_status()


download = download2

if __name__ == '__main__':
    print download("http://example.webscraping.com")

# -*- coding:utf-8 -*-
"""
refactor common.py with Requests(http://cn.python-requests.org/zh_CN/latest/)
"""
import urlparse
import time
from datetime import datetime

import requests


class Downloader(object):
    def __init__(self, cache=None, delay=1, user_agent='wswp',
                 proxies=None, timeout=5, debug=False):
        self.throttle = Throttle(delay)
        self.user_agent = user_agent
        self.proxies = proxies
        self.timeout = timeout
        self.debug = debug
        self.cache = cache

    def __call__(self, url):
        result = None
        if self.cache:
            try:
                result = self.cache[url]
                print url, "is cached"
            except KeyError:
                pass
        if result is None:
            self.throttle.wait(url)
            headers = {'user-agent': self.user_agent}
            result = self.download(url, headers, self.proxies, self.timeout,
                                   self.debug)
            if self.cache:
                self.cache[url] = result
        return result['html']

    def download(self, url, headers, proxies, timeout, debug):
        print 'Downloading:', url
        r = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
        if debug:
            print r.request.headers
            print r.headers
        if r.status_code == 200:
            return {'html': r.text, 'code': r.status_code}
        else:
            print "Download failed"
            r.raise_for_status()


class Throttle(object):
    def __init__(self, delay):
        self.delay = delay
        self.domains = {}

    def wait(self, url):
        domain = urlparse.urlparse(url).netloc
        last_accessed = self.domains.get(domain)

        if self.delay > 0 and last_accessed is not None:
            sleep_time = self.delay\
                         - (datetime.now() - last_accessed).seconds
            if sleep_time > 0:
                time.sleep(sleep_time)
        self.domains[domain] = datetime.now()


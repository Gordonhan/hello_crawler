# -*- coding:utf-8 -*-
"""
refactor common.py with Requests(http://cn.python-requests.org/zh_CN/latest/)
"""
import urlparse
import time
from datetime import datetime

import requests

from util import get_header


class Downloader(object):
    def __init__(self, cache=None, delay=1, proxies=None, timeout=5,
                 debug=False):
        self.throttle = Throttle(delay)
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
            # 随机生成请求首部
            headers = get_header()
            result = self.download(url, headers, self.proxies, self.timeout,
                                   self.debug)
            if self.cache:
                self.cache[url] = result
        return result['html']

    def download(self, url, headers, proxies, timeout, debug):
        print 'Downloading:', url
        r = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
        # chardet 真他妈的慢
        # r.encoding = chardet.detect(r.content)['encoding']
        if debug:
            print r.request.headers
            print r.headers
        if r.status_code == 200:
            return {'html': decode_content(r), 'code': r.status_code}
        else:
            print "Download failed"
            r.raise_for_status()


def decode_content(r):
    """自行对 requests 返回的二进制响应内容进行解码，以避免乱码问题"""
    encoding = r.encoding
    # requests 会基于响应首部信息（Content-Type）自动对响应内容进行解码
    # 如果该信息缺失，默认使用ISO-8859-1进行解码
    if encoding == 'ISO-8859-1':
        # 查找响应页面<header>标签中设置的编码
        encodings = requests.utils.get_encodings_from_content(r.text)
        # 如果上一步能查找出编码，则用之，否则查找响应首部设置的编码
        encoding = encodings[0] if encodings else r.apparent_encoding
    # return r.content.decode(encoding, 'replace').encode('utf-8', 'replace')
    # 对二进制响应内容进行解码
    r.content.decode(encoding, 'replace')


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

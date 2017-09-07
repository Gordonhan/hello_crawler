# -*- coding:utf-8 -*-
"""
refactor common.py with requests
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
    # chardet 真他妈的慢
    # r.encoding = chardet.detect(r.content)['encoding']

    if debug:
        print r.request.headers
        print r.headers

    if r.status_code == 200:
        return decode_content(r)
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
        # 如果上一步能查找出编码，则用之，否则使用chardet对响应内容进行推断
        # 备注：r.apparent_encoding 内部使用chardet
        encoding = encodings[0] if encodings else r.apparent_encoding
    # return r.content.decode(encoding, 'replace').encode('utf-8', 'replace')
    # 对二进制响应内容进行解码
    return r.content.decode(encoding, 'replace')


download = download2

if __name__ == '__main__':
    print download("http://example.webscraping.com")

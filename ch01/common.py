# -*- coding:utf-8 -*-
import urllib
import urllib2
import urlparse


def download1(url):
    return urllib2.urlopen(url).read()


def download2(url, num_retries=2):
    print "Downloading:", url
    html = None
    try:
        html = urllib2.urlopen(url).read()
    except urllib2.URLError, e:
        print "Download error:", e.reason
        if num_retries > 0:
            if hasattr(e, "code") and 500 <= e.code < 600:
                html = download2(url, num_retries=num_retries-1)
    return html


def download3(url, user_agent='wswp', num_retries=2):
    print "Downloading:", url
    request = urllib2.Request(url)
    request.add_header('user_agent', user_agent)

    html = None
    try:
        html = urllib2.urlopen(request).read()
    except urllib2.URLError, e:
        print "Download error:", e.reason
        if num_retries > 0:
            if hasattr(e, "code") and 500 <= e.code < 600:
                html = download2(url, num_retries=num_retries-1)
    return html


def download4(url, user_agent='wswp', headers=None, proxy=None, data=None,
              timeout=5, num_retries=2, debug=False):
    print "Downloading:", url
    headers = headers or {}
    headers['user-agent'] = user_agent
    if debug:
        opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=1),
                                      urllib2.HTTPSHandler(debuglevel=1))
    else:
        opener = urllib2.build_opener()
    if proxy:
        proxy_param = {urlparse.urlparse(url).scheme: proxy}
        opener.add_handler(urllib2.ProxyHandler(proxy_param))
    if data:
        data = urllib.urlencode(data)

    request = urllib2.Request(url, headers=headers)
    html = None
    try:
        html = opener.open(request, data=data, timeout=timeout).read()
    except urllib2.URLError, e:
        print "Download error:", e.reason
        if num_retries > 0:
            if hasattr(e, "code") and 500 <= e.code < 600:
                html = download2(url, num_retries=num_retries-1)
    return html

download = download4

if __name__ == '__main__':
    # print download('http://example.webscraping.com')
    print download('http://httpstat.us/500', debug=True)
    # download('http://httpstat.us/200', data={'sleep': 6000}, debug=True)
    # print download('https://www.qiushibaike.com/qiushi/',
    #               user_agent="Yisouspider")
    #download('http://example.webscraping.com', debug=True, user_agent="wswp",
    #         proxy="116.54.28.141:80")

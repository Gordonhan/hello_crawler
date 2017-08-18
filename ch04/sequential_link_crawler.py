# -*- coding:utf-8 -*-
import re
import urlparse
import csv

import datetime

from cache import MongoCache
from downloader import Downloader


def link_crawler(seed_url, link_regex=None, proxies=None,
                 delay=1, max_depth=-1, max_urls=-1, timeout=5,
                 cache=None, scraping_callback=None, debug=False):
    num_urls = 0

    crawl_queue = []
    seen = {seed_url: 0}

    # 读取topsite.csv，将排行榜的网站url保存到爬取队列
    with open('topsite.csv', 'rb') as f:
        csv_reader = csv.reader(f)
        csv_reader.next()
        for _, website in csv_reader:
            crawl_queue.append(website)

    crawl_queue.reverse()

    d = Downloader(cache=cache, delay=delay,
                   proxies=proxies, timeout=timeout, debug=debug)
    while crawl_queue:
        url = crawl_queue.pop()
        try:
            d(url)
        except:
            pass

        '''
        if scraping_callback:
            scraping_callback(url, html)

        depth = seen[url]
        if depth != max_depth:
            if link_regex:
                links = [link for link in get_links(html)
                         if match(link, link_regex)]

            for link in links:
                link = normalize(seed_url, link)
                if link not in seen:
                    crawl_queue.append(link)
                    seen[link] = depth + 1
         '''
        num_urls += 1
        if num_urls == max_urls:
            break


def same_domain(seed_url, url):
    return urlparse.urlparse(seed_url).netloc == urlparse.urlparse(url).netloc


def normalize(seed_url, link):
    components = urlparse.urlparse(seed_url)
    return urlparse.urljoin(components.scheme + "://" + components.netloc, link)


def get_links(html):
    web_page = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    return web_page.findall(html)


def match(link, link_regex):
    if link_regex is None:
        return False
    return re.search(link_regex, link)


if __name__ == "__main__":
    start = datetime.datetime.now()
    link_crawler(seed_url="http://top.chinaz.com/alltop/",
                 link_regex=None,
                 delay=2,
                 max_depth=-1,
                 max_urls=330,
                 timeout=10,
                 cache=MongoCache('topsite', 'top1t')
                 )
    end = datetime.datetime.now()
    print 'cost', (end - start).seconds, 's'

# -*- coding:utf-8 -*-
import re
import urlparse
import csv
import threading
import time
import datetime

from cache import MongoCache
from downloader import Downloader

MAX_THREADS = 5
SLEEP_TIME =1


def link_crawler(seed_url, link_regex=None, proxies=None,
                 delay=1, max_depth=-1, max_urls=-1, timeout=5,
                 cache=None, scraping_callback=None, debug=False):
    num_urls = 0
    crawl_queue = []

    # 读取topsite.csv，将排行榜的网站url保存到爬取队列
    with open('topsite.csv', 'rb') as f:
        csv_reader = csv.reader(f)
        csv_reader.next()
        for _, website in csv_reader:
            crawl_queue.append(website)

    crawl_queue.reverse()

    d = Downloader(cache=cache, delay=delay,
                   proxies=proxies, timeout=timeout, debug=debug)

    def thread_crawl():
        while True:
            try:
                url = crawl_queue.pop()
            except IndexError:
                break
            else:
                d(url)

    threads = []
    while threads or crawl_queue:
        for thread in threads:
            if not thread.is_alive():
                threads.remove(thread)
        while len(threads) < MAX_THREADS and crawl_queue:
            t = threading.Thread(target=thread_crawl)
            threads.append(t)
            t.setDaemon(True)
            t.start()
        time.sleep(SLEEP_TIME)


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
    link_crawler(seed_url="http://top.chinaz.com/alltop/",
                 link_regex=None,
                 delay=2,
                 max_depth=-1,
                 max_urls=330,
                 timeout=10,
                 cache=MongoCache('topsite', 'top1t.thread')
                 )

# -*- coding:utf-8 -*-
import re
import urlparse
import csv
import threading
import time
import multiprocessing

from cache import MongoCache
from downloader import Downloader
from mongo_queue import MongoQueue

SLEEP_TIME =1


def link_crawler(seed_url, link_regex=None, proxies=None, delay=1, max_depth=-1,
                 max_urls=-1, timeout=5, cache=None, scraping_callback=None,
                 max_threads=10, debug=False):
    crawl_queue = MongoQueue('topsite', 'cralw_queue')

    # 读取topsite.csv，将排行榜的网站url保存到爬取队列
    with open('topsite.csv', 'rb') as f:
        csv_reader = csv.reader(f)
        csv_reader.next()
        for _, website in csv_reader:
            crawl_queue.push(website)

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
                crawl_queue.complete(url)

    threads = []
    while threads or crawl_queue:
        for thread in threads:
            if not thread.is_alive():
                threads.remove(thread)
        while len(threads) < max_threads and crawl_queue:
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


def process_crawl(*args, **kw):
    nums_cpu = multiprocessing.cpu_count()
    print 'starting {0} processes'.format(nums_cpu)
    processes = []
    for i in range(nums_cpu):
        p = multiprocessing.Process(target=link_crawler, args=args, kwargs=kw)
        p.start()
        processes.append(p)
    for p in processes:
        p.join()


if __name__ == "__main__":
    process_crawl(
        "http://top.chinaz.com/alltop/",
        link_regex=None,
        delay=2,
        max_depth=-1,
        max_urls=330,
        timeout=10,
        max_threads=4,
        cache=MongoCache('topsite', 'top1t.process')
    )

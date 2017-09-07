# -*- coding:utf-8 -*-
import re
import urlparse
import robotparser
import datetime
import threading
import time


from cache import MongoCache
from downloader import Downloader
from scraping_callback import ScrapingCallback


def link_crawler(seed_url, link_regex=None, proxies=None,
                 delay=1, max_depth=-1, timeout=5, max_thread=5, sleep_time=1,
                 cache=None, scraping_callback=None, debug=False):
    crawl_queue = [seed_url]
    seen = {seed_url: 0}

    d = Downloader(cache=cache, delay=delay,
                   proxies=proxies, timeout=timeout, debug=debug)

    def thread_crawl():
        while True:
            try:
                url = crawl_queue.pop()
                html = d(url)
            except IndexError:
                break
            except Exception:
                pass
            else:
                links = scraping_callback(url,  html) if scraping_callback else []
                depth = seen[url]
                if depth != max_depth:
                    links = [normalize(seed_url, link) for link
                             in get_links(html) if match(link, link_regex)] \
                        if link_regex else links
                    for link in links:
                        if link not in seen:
                            crawl_queue.append(link)
                            seen[link] = depth + 1

    threads = []
    while threads or crawl_queue:
        for thread in threads:
            if not thread.is_alive():
                threads.remove(thread)
        while len(threads) < max_thread and crawl_queue:
            t = threading.Thread(target=thread_crawl)
            t.setDaemon(True)
            t.start()
            threads.append(t)
        time.sleep(sleep_time)


def get_robots(url):
    rp = robotparser.RobotFileParser()
    rp.set_url(urlparse.urljoin(url, '/robots.txt'))
    try:
        rp.read()
    except IOError:
        print "Can't read robots.txt"
        return None
    else:
        return rp


def same_domain(seed_url, url):
    return urlparse.urlparse(seed_url).netloc == urlparse.urlparse(url).netloc


def normalize(seed_url, link):
    link, _ = urlparse.urldefrag(link)
    return urlparse.urljoin(seed_url, link)


def get_links(html):
    web_page = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    return web_page.findall(html)


def match(link, link_regex):
    if link_regex is None:
        return False
    return re.search(link_regex, link)


if __name__ == "__main__":
    start = datetime.datetime.now()
    link_crawler(seed_url="http://example.webscraping.com",
                 link_regex=None,
                 delay=-1,
                 max_depth=-1,
                 timeout=10,
                 cache=MongoCache(),
                 scraping_callback=ScrapingCallback(1000)
                 )
    end = datetime.datetime.now()
    print 'cost', (end - start).seconds, 's'

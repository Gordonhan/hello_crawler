# -*- coding:utf-8 -*-
import re
import urlparse
import robotparser
import datetime

from cache import MongoCache
from downloader import Downloader
from scraping_callback import ScrapingCallback


def link_crawler(seed_url, link_regex=None, proxies=None,
                 delay=1, max_depth=-1, timeout=5,
                 cache=None, scraping_callback=None, debug=False,):

    crawl_queue = [seed_url]
    seen = {seed_url: 0}

    d = Downloader(cache=cache, delay=delay,
                   proxies=proxies, timeout=timeout, debug=debug)
    while crawl_queue:
        url = crawl_queue.pop()
        try:
            html = d(url)
        except Exception: pass
        else:
            links = scraping_callback(url, html) if scraping_callback else []
            depth = seen[url]
            if depth != max_depth:
                links = [normalize(seed_url, link) for link in get_links(html)
                         if match(link, link_regex)] if link_regex else links
                for link in links:
                    if link not in seen:
                        crawl_queue.append(link)
                        seen[link] = depth + 1


def get_robots(url):
    rp = robotparser.RobotFileParser()
    components = urlparse.urlparse(url)
    rp.set_url(
        urlparse.urljoin(
            components.scheme + "://" + components.netloc, '/robots.txt'
        )
    )
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
    link_crawler(seed_url="http://example.webscraping.com",
                 link_regex=None,
                 delay=-1,
                 max_depth=-1,
                 timeout=10,
                 cache=MongoCache('topsite', 'top1t'),
                 scraping_callback=ScrapingCallback(1000)
                 )
    end = datetime.datetime.now()
    print 'cost', (end - start).seconds, 's'

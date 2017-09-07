# -*- coding:utf-8 -*-
import re
import robotparser
import urlparse
import pymongo

from cache import MongoCache
from downloader import Downloader
from scraping_callback import ScrapingCallback


def link_crawler(seed_url, link_regex=None, user_agent="wswp", proxies=None,
                 delay=1, max_depth=-1, max_urls=-1, timeout=5,
                 cache=None, scraping_callback=None, debug=False,
                 follow_robot=False):
    num_urls = 0

    crawl_queue = [seed_url]
    seen = {seed_url: 0}

    d = Downloader(cache=cache, delay=delay, user_agent=user_agent,
                   proxies=proxies, timeout=timeout, debug=debug)
    rp = get_robots(seed_url)
    while crawl_queue:
        url = crawl_queue.pop()
        if follow_robot:
            if not (rp is None or rp.can_fetch(user_agent, url)):
                print 'Blocked by robots.txt:', url
                continue

        html = d(url)
        if scraping_callback:
            scraping_callback(url, html)

        depth = seen[url]
        if depth != max_depth:
            links = [normalize(seed_url, link) for link in get_links(html) if match(link, link_regex)] if link_regex else []
            for link in links:
                if same_domain(seed_url, link) and link not in seen:
                    crawl_queue.append(link)
                    seen[link] = depth + 1

        num_urls += 1
        if num_urls == max_urls:
            break


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
    return re.match(link_regex, link)


if __name__ == "__main__":
    client = pymongo.MongoClient('localhost', 27017)
    mongo_cache = MongoCache(client=client)
    link_crawler(seed_url="http://example.webscraping.com",
                 link_regex="/places/default/(view|index)",
                 delay=1,
                 max_depth=-1,
                 cache=mongo_cache,
                 scraping_callback=ScrapingCallback(),
                 )

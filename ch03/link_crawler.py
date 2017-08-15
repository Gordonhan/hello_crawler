# -*- coding:utf-8 -*-
import re
import urlparse
import requests

from cache import MongoCache
from downloader import Downloader
from scraping_callback import ScrapingCallback


def link_crawler(seed_url, link_regex=None, user_agent="wswp", proxies=None,
                 delay=1, max_depth=-1, max_urls=-1, timeout=5,
                 cache=None, scraping_callback=None, debug=False):
    num_urls = 0

    crawl_queue = [seed_url]
    seen = {seed_url: 0}

    d = Downloader(cache=cache, delay=delay, user_agent=user_agent,
                   proxies=proxies, timeout=timeout, debug=debug)
    while crawl_queue:
        url = crawl_queue.pop()

        try:
            html = d(url)
        except requests.exceptions.HTTPError:
            continue
        except requests.exceptions.Timeout:
            continue

        if scraping_callback:
            scraping_callback(url, html)

        depth = seen[url]
        if depth != max_depth:
            if link_regex:
                links = [link for link in get_links(html)
                         if match(link, link_regex)]

            for link in links:
                link = normalize(seed_url, link)
                if same_domain(seed_url, link) and link not in seen:
                    crawl_queue.append(link)
                    seen[link] = depth + 1

        num_urls += 1
        if num_urls == max_urls:
            break
    print num_urls


def same_domain(seed_url, url):
    return urlparse.urlparse(seed_url).netloc == urlparse.urlparse(url).netloc


def normalize(seed_url, link):
    components = urlparse.urlparse(seed_url)
    return urlparse.urljoin(components.scheme + "://" + components.netloc, link)


def get_links(html):
    web_page = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    return web_page.findall(html)


def match(link, link_regex):
    return re.match(link_regex, link)


if __name__ == "__main__":
    mongo_cache = MongoCache()
    link_crawler(seed_url="http://example.webscraping.com",
                 link_regex="/places/default/(view|index)",
                 delay=1,
                 max_depth=-1,
                 cache=mongo_cache,
                 scraping_callback=ScrapingCallback(),
                 )

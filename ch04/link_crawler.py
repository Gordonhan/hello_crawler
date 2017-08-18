# -*- coding:utf-8 -*-
"""抓取http://top.chinaz.com/alltop/的中文网站排行榜，并保存到topsite.csv"""
import re
import urlparse

from cache import MongoCache
from downloader import Downloader
from scraping_callback import ScrapingCallback


def link_crawler(seed_url, link_regex=None, proxies=None,
                 delay=1, max_depth=-1, max_urls=-1, timeout=5,
                 cache=None, scraping_callback=None, debug=False):
    regex = link_regex
    num_urls = 0

    crawl_queue = [seed_url]
    seen = {seed_url: 0}

    d = Downloader(cache=cache, delay=delay,
                   proxies=proxies, timeout=timeout, debug=debug)
    while crawl_queue:
        url = crawl_queue.pop()
        html = d(url)

        if scraping_callback:
            scraping_callback(url, html)

        depth = seen[url]
        if depth != max_depth:
            if link_regex:
                link_regex = regex.format(num_urls + 2)
                links = [link for link in get_links(html)
                         if match(link, link_regex)]

            for link in links:
                link = normalize(seed_url, link)
                if link not in seen:
                    crawl_queue.append(link)
                    seen[link] = depth + 1

        num_urls += 1
        if num_urls == max_urls:
            break


def same_domain(seed_url, url):
    return urlparse.urlparse(seed_url).netloc == urlparse.urlparse(url).netloc


def normalize(seed_url, link):
    # components = urlparse.urlparse(seed_url)
    # return urlparse.urljoin(components.scheme + "://" + components.netloc, link)
    return urlparse.urljoin('http://search.top.chinaz.com', link)


def get_links(html):
    web_page = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    return web_page.findall(html)


def match(link, link_regex):
    # return re.match(link_regex, link)
    return re.search(link_regex, link)


if __name__ == "__main__":
    link_crawler(seed_url="http://top.chinaz.com/alltop/",
                 link_regex="/top\.aspx\?p={}&t=all",
                 delay=2,
                 max_depth=-1,
                 timeout=5,
                 cache=MongoCache('topsite', 'source'),
                 scraping_callback=ScrapingCallback(),
                 )

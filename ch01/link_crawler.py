# -*- coding:utf-8 -*-
import re
import urlparse
from datetime import datetime
import time

from common_refactor import download


def link_crawler(seed_url, link_regex=None, user_agent="wswp", headers=None,
                 proxies=None, delay=1, max_depth=-1, max_urls=-1, timeout=5,
                 debug=False):
    num_urls = 0

    crawl_queue = [seed_url]
    seen = {seed_url: 0}

    throttle = Throttle(delay)
    while crawl_queue:
        url = crawl_queue.pop()

        throttle.wait(url)
        html = download(url, user_agent=user_agent, headers=headers,
                        proxies=proxies, timeout=timeout, debug=debug)

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

        num_urls += 1
        if num_urls == max_urls:
            break


class Throttle(object):
    def __init__(self, delay):
        self.delay = delay
        self.domains = {}

    def wait(self, url):
        domain = urlparse.urlparse(url).netloc
        last_accessed = self.domains.get(domain)

        if self.delay > 0 and last_accessed is not None:
            sleep_time = self.delay\
                         - (datetime.now() - last_accessed).seconds
            if sleep_time > 0:
                time.sleep(sleep_time)
        self.domains[domain] = datetime.now()


def some_domain(seed_url, url):
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
    link_crawler(seed_url="http://example.webscraping.com",
                 link_regex="/places/default/(view|index)",
                 delay=1,
                 max_depth=1)
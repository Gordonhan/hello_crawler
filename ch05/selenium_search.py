# -*- coding:utf-8 -*-
"""
@author: Gordon Han
@contact: Gordon-Han@hotmail.com
"""
from selenium import webdriver


def main():
    driver = webdriver.Firefox()
    driver.get('http://example.webscraping.com/places/default/search')

    driver.find_element_by_id('search_term').send_keys('.')
    js = "document.getElementById('page_size').options[1].text='1000'"
    driver.execute_script(js)
    driver.find_element_by_id('search').click()

    driver.implicitly_wait(30)

    links = driver.find_elements_by_css_selector("#results a")
    for link in links:
        print link.get_property('href')
        print link.text


if __name__ == '__main__':
    main()

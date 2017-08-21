# -*- coding:utf-8 -*-
import requests
import lxml.html


LOGIN_URL = 'http://example.webscraping.com/places/default/user/login'
LOGIN_EMAIL = 'example@webscraping.com'
LOGIN_PASSWORD = 'example'


def login_basic():
    data = {'email': LOGIN_EMAIL, 'password': LOGIN_PASSWORD}
    response = requests.post(LOGIN_URL, data=data)
    print response.url


def login_formkey():
    html = requests.get(LOGIN_URL).text
    data = parse_html(html)
    data['email'] = LOGIN_EMAIL
    data['password'] = LOGIN_PASSWORD
    response = requests.post(LOGIN_URL, data=data)
    print response.url


def login_cookie():
    '''
    response = requests.get(LOGIN_URL)
    html = response.text
    cookies = response.cookies
    data = parse_html(html)
    data['email'] = LOGIN_EMAIL
    data['password'] = LOGIN_PASSWORD
    response = requests.post(LOGIN_URL, data=data, cookies=cookies)
    print response.url
    '''

    s = requests.session()
    html = s.get(LOGIN_URL).text
    data = parse_html(html)
    data['email'] = LOGIN_EMAIL
    data['password'] = LOGIN_PASSWORD
    s.post(LOGIN_URL, data=data)
    return s


def parse_html(html):
    tree = lxml.html.fromstring(html)
    data = {}
    for e in tree.cssselect('form input'):
        if e.get('name'):
            data[e.get('name')] = e.get('value')
    return data


if __name__ == '__main__':
    login_cookie()

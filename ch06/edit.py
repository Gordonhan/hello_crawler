# -*- coding:utf-8 -*-
import lxml.html

import login

COUNTRY_URL = 'http://example.webscraping.com/places/default/edit/Afghanistan-1'


def edit_country():
    s = login.login_cookie()
    html = s.get(COUNTRY_URL).text
    data = login.parse_html(html)
    print '修改前的人口：', data['population']

    data['population'] = int(data['population']) + 1
    html = s.post(COUNTRY_URL, data=data).text
    tree = lxml.html.fromstring(html)
    e = tree.cssselect('tr#places_population__row > td.w2p_fw')[0]
    print '修改后的人口：', e.text_content()


if __name__ == '__main__':
    edit_country()

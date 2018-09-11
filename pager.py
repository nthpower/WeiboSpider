#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author nthpower
# @date 2018-09-10 11:10

from urllib import parse


class WeiboPage:
    body = {
        'pre_page': '0',
        'page': 1,
        'pagebar': '0'
    }

    def __init__(self, sid, _page=1):
        self._url = 'https://weibo.com/{sid}?from=otherprofile&is_all=1&'.format(sid=sid)
        WeiboPage.body['page'] = _page

    def first(self):
        WeiboPage.body['pre_page'] = WeiboPage.body['page'] - 1
        url = self._url + parse.urlencode(WeiboPage.body)
        print("=> first_page: %s" % url)
        return url

    def second(self):
        WeiboPage.body['pagebar'] = '0'
        WeiboPage.body['pre_page'] = WeiboPage.body['page']
        url = self._url + parse.urlencode(WeiboPage.body)
        print("=> second_page: %s" % url)
        return url

    def third(self):
        WeiboPage.body['pagebar'] = '1'
        WeiboPage.body['pre_page'] = WeiboPage.body['page']
        url = self._url + parse.urlencode(WeiboPage.body)
        print("=> third_page: %s" % url)
        return url


if __name__ == '__main__':
    page = WeiboPage('rmrb', 1)
    page.first()
    page.second()
    page.third()

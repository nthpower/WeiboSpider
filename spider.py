#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author nthpower
# @date 2018-09-10 11:30

import os
import random
import re
import time

import requests
from bs4 import BeautifulSoup

import settings
from login import WeiboLogin
from pager import WeiboPage
from parser import WeiboParser

# 这里将User-Agent设置为spider便可以爬取到内容，并且不需要cookies
# 若是换成其他的值，则获取文章的途径会有所改变
USER_AGENT = 'spider'


class Spider:

    def __init__(self, sid):
        self._sid = sid
        self._login = WeiboLogin(settings.ACCOUNT, settings.PASSWORD)

        # 将抓取的内容保存在 以博主ID号为文件夹 的目录下
        self._dir = 'resource/' + sid
        self._parser = WeiboParser(self._dir)

    def __spider(self, url):
        cookies = self._login.cookies()
        # 获取登录cookies
        if not cookies:
            if not self._login.login():
                print("==> login failed and exist!")
                exit(-1)

        headers = {
            'User-Agent': USER_AGENT
        }

        # 请求URL，获取页面信息，其中包含文章内容
        response = requests.get(url, cookies=cookies, headers=headers)
        if response.status_code != 200:
            print('network error')
            return

        # re.S 匹配包括换行在内的所有字符，这样就不会因为换行导致的匹配不到内容
        match = re.search('Sina Visitor System', response.text, re.S)
        if not match:
            # 登录成功，开始解析文章内容
            content = BeautifulSoup(response.text, 'lxml', exclude_encodings='gbk')
            self._parser.parse(content)
            print("match")
        else:
            print('<Sina Visitor System> error')

    def running(self, start_page, end_page):
        print("*" * 50)
        print("*" + " Start crawling sina")
        print("*" + " Account: %s" % settings.ACCOUNT)
        print("*" + " Sid: %s" % self._sid)
        print("*" + " page: %d - %d" % (start_page, end_page))
        print("*" * 50)

        # 检测保存目录是否存在，不存在则创建
        if not os.path.exists(self._dir):
            os.makedirs(self._dir)

        for i in range(start_page, end_page + 1):
            _pager = WeiboPage(self._sid, i)
            print("===> START Page <%d --- 1>" % i)
            self.__spider(_pager.first())
            print("===> END Page <%d --- 1>" % i)

            print("===> START Page <%d --- 2>" % i)
            self.__spider(_pager.second())
            print("===> END Page <%d --- 2>" % i)

            print("===> START Page <%d --- 3>" % i)
            self.__spider(_pager.third())
            print("===> END Page <%d --- 3>" % i)

            if i != end_page:
                time_random = random.randint(10, 20)
                print("==> Sleep %d second" % (time_random + 10))
                time.sleep(time_random + 10)


if __name__ == '__main__':
    spider = Spider('rmrb')
    spider.running(1, 1)

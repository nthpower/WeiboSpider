#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import binascii
import json
import os
import re
from urllib import parse

import rsa
from requests import Session

import settings
import utils

USER_AGENT = settings.USER_AGENT

# 在登录之前请求服务器，获取登录时POST的必要参数
URL_SERVER_TIME = 'https://login.sina.com.cn/sso/prelogin.php?entry=sso&callback=sinaSSOController' \
                    '.preloginCallBack&su={user}&rsakt=mod&client=ssologin.js(v1.4.15)&_={time}'
# 登录url
URL_LOGIN = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)&_={time}'

HEADERS = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
    'Connection': 'keep-alive',
    'Host': 'login.sina.com.cn',
    'Referer': 'https://login.sina.com.cn/signup/signin.php?entry=sso',
    'User-Agent': USER_AGENT
}


class WeiboLogin:

    def __init__(self, user, password):
        self.__session = Session()  # 登录会话
        self.__user = user
        self.__password = password
        self.__file = 'cookies/' + user
        self.__cookies = None

    def __encode_user__(self):
        _user = parse.quote(self.__user)
        return base64.encodebytes(_user.encode())[:-1].decode()

    def __password__(self, _time, _nonce, _pubkey):
        _key = rsa.PublicKey(int(_pubkey, 16), int('10001', 16))
        _data = str(_time) + '\t' + str(_nonce) + '\n' + str(self.__password)
        _pwd = rsa.encrypt(_data.encode(), _key)
        return binascii.b2a_hex(_pwd)

    def __server_time__(self, encode_user):
        url = URL_SERVER_TIME.format(user=encode_user, time=utils.timeMillis())

        response = self.__session.get(url, headers=HEADERS)
        content = response.text
        p = re.compile('({.*})')
        try:
            json_data = p.search(str(content)).group(1)
            data = json.loads(json_data)
            server_time = str(data['servertime'])
            nonce = data['nonce']
            pubkey = data['pubkey']
            rsakv = data['rsakv']
            return server_time, nonce, pubkey, rsakv
        except:
            print('=> Get severtime error!')
            return None

    @classmethod
    def __post_data__(cls, encode_user, encode_pwd, servertime, nonce, rsakv):
        return {
            'useticket': '0',
            'gateway': '1',
            'vsnf': '1',
            'cdult': '3',
            'nonce': nonce,
            'savestate': '30',
            'sr': '1911*924',
            'rsakv': rsakv,
            'servertime': servertime,
            'su': encode_user,
            'sp': encode_pwd,
            'from': 'null',
            'pwencode': 'rsa2',
            'domain': 'sina.com.cn',
            'entry': 'sso',
            'service': 'sso',
            'returntype': 'TEXT',
            'encoding': 'UTF-8'
        }

    def login(self):
        result = False
        encode_user = self.__encode_user__()
        server_time, nonce, pubkey, rsakv = self.__server_time__(encode_user)

        encode_pwd = self.__password__(server_time, nonce, pubkey)
        post_data = self.__post_data__(encode_user, encode_pwd, server_time, nonce, rsakv)

        url = URL_LOGIN.format(time=utils.timeMillis())
        response = self.__session.post(url, data=post_data, headers=HEADERS)
        if response.status_code == 200:
            data = json.loads(response.text)
            result = data['retcode']
            if result == '0':  # retcode的值为0，表示登录成功
                result = True
                self.__save__(self.__session.cookies)
                print('=> Login successful')
            else:
                print('=> Login failed')
        else:
            print("=> network error")

        return result

    def cookies(self):
        if self.__cookies:
            print('=> read cookies from cache')
            return self.__cookies

        if os.path.isfile(self.__file):
            print('=> read cookies from local file')
            with open(self.__file, "r") as file:
                self.__cookies = json.loads(file.read())
                file.close()
        return self.__cookies

    def __save__(self, cookies):
        _dir = os.path.dirname(self.__file)
        if not os.path.exists(_dir):
            os.makedirs(_dir)

        if os.path.isfile(self.__file):
            os.remove(self.__file)

        _dict = {}
        for cookie in cookies:
            _dict[cookie.name] = cookie.value

        self.__cookies = _dict
        with open(self.__file, "w") as file:
            file.write(json.dumps(_dict))
            file.close()


if __name__ == '__main__':
    login = WeiboLogin(settings.ACCOUNT, settings.PASSWORD)
    login.login()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author nthpower
# @date 2018-09-10 16:54
import os
import re
import shutil
import time
from urllib import parse
from urllib import request

"""
文章爬取标志位
1. 如果文章目录下存在此文件，表示此文章未爬取完成，需要重新爬取
2. 如果文章目录下不存在此文件，表示文章爬取成功，可以跳过
"""
SPIDER_GUARD_FILE = '.GUARD_FILE'


class WeiboParser:

    def __init__(self, sid_dir):
        self.__dir = sid_dir

    def parse(self, article):
        # 根据‘WB_detail’关键字，查找文章
        for article in article.find_all("div", class_="WB_detail"):
            print("=>" + ("*" * 25))

            # 获取文章发布时间
            date_find = article.find("a", attrs={"date": True})
            date = date_find['date']

            print("=> date: " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(date) / 1000)))

            # 以文章发布时间作为文章目录，此文章所有资源都会保存在此目录下
            _article_dir = self.__dir + "/" + date
            _flag_file = _article_dir + "/" + SPIDER_GUARD_FILE
            if not os.path.exists(_article_dir):
                os.makedirs(_article_dir)
                # 创建文章目录时，一并创建标志位文件
                open(_flag_file, "w").close()
            else:
                # 存在文章目录，检查是否存在标志位文件
                if os.path.isfile(_flag_file):
                    # 存在标志位文件，删除文章目录，重新爬取
                    shutil.rmtree(_article_dir)
                    os.makedirs(_article_dir)
                    open(_flag_file, "w").close()
                else:
                    print("=> <SKIP> exist and skip")
                    continue

            expand = article.find("div", class_="WB_feed_expand")
            if expand:
                # 未找到‘WB_feed_expand’标签，此条文章为原创
                self.__parse_article(expand, _article_dir)
                pass
            else:
                # 找到‘WB_feed_expand’标签，此条文章为转发
                self.__parse_article(article, _article_dir)
                pass

    @classmethod
    def __parse_article(cls, article, article_dir):
        """
        解析文章
        :param article:
        :param article_dir:
        :return:
        """
        title_file = article_dir + "/title.txt"
        image_dir = article_dir + "/image"

        if not os.path.exists(image_dir):
            os.makedirs(image_dir)

        # 待下载资源列表
        image_download = []

        # 查找微博标题
        title = ""
        for item in article.find("div", class_="WB_text").children:
            _temp = str(item.string).strip()
            if _temp != "None":
                title = title + _temp

        print("=> title: " + title)
        # 将文章标题写入文件
        with open(title_file, "w") as file:
            file.write(title)
            file.close()

        # 查找多媒体文件显示区域
        media_box = article.find("div", class_="media_box")

        # 先查找ul标签里面的action-data属性，如果没有，则继续查找li标签里面的action-data属性
        # 通常情况下，如果ul中有action-data属性，则表明，此条微博的内容由图片或是动图构成
        # 如果ul中存在gif图片，则需要在li中查找对应的源视频下载路径
        # 如果ul中不存在action-data属性，而是在li中，则表情此条微博内容为外部视频
        if not media_box:
            print("=> ERROR: not has media file, SKIP")
            return

        action_data_find = media_box.find("ul", attrs={'action-data': True})
        if action_data_find:
            # ul标签中存在action-data数据，则解析action-data中的高清大图
            is_gif = False
            image_str = ''
            data = action_data_find['action-data']
            data_split = str.split(data, "&")
            for item in data_split:
                for match in re.findall('clear_picSrc=(.*)', item):
                    if match:
                        image_str = match
            if image_str:
                # 查找到图片信息，进一步解析图片
                images = str.split(image_str, ",")
                for image in images:
                    # 将图片加入下载队列
                    image_download.append(image)

                    # 检查是否存在后缀名为gif的图片，如果存在，则需要进一步解析gif原视频
                    if str.endswith(image, ".gif"):
                        is_gif = True  # 存在gif图片，置标志位为true，后续解析gif
            else:
                print("empty")

            # 获取gif原视频链接
            if is_gif:
                li_find = media_box.find_all("li", attrs={'action-data': True})
                for item in li_find:
                    if item is None:
                        continue
                    data = item['action-data']
                    data_split = str.split(data, "&")
                    for data_item in data_split:
                        for match in re.findall('gif_url=(.*)', data_item):
                            if match:
                                image_download.append(match)

        else:
            li_find = media_box.find_all("li", attrs={'action-data': True})
            for item in li_find:
                if item is None:
                    continue
                data = item['action-data']
                data_split = str.split(data, "&")
                for data_item in data_split:
                    for match in re.findall('video_src=(.*)', data_item):
                        if match:
                            _temp = match.split("https%3A")
                            _url = _temp[len(_temp) - 1].strip()
                            # print("==> video url: %s" % _url)
                            image_download.append(_url)

        # 下载资源
        for item in image_download:
            item = parse.unquote_plus(item)
            # print("item: %s" % item)
            __split = item.split("?")[0].split("/")
            filename = __split[len(__split) - 1]
            print("=> download: " + filename)
            file_path = image_dir + "/" + filename
            try:
                req = request.urlopen("https:" + item)
                data = req.read()
                with open(file_path, 'wb') as f:
                    f.write(data)
                    f.close()
            except:
                print("==> ERROR: download failed, skip <%s>" % item)

        os.remove(article_dir + "/" + SPIDER_GUARD_FILE)
        print("=> FINISH~~~")

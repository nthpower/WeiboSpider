#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author nthpower
# @date 2018-09-11 08:47

from spider import Spider
from settings import SID


if __name__ == '__main__':
    for sid, start, end in SID:
        spider = Spider(sid)
        spider.running(start, end)

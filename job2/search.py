#!/usr/bin/python3

# -*- Mode: Python; coding: utf-8; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*- 
#
# search.py
# Copyleft 2014 Yuzo(PillowSky) <Yuzo@pillowsky.org>
# Compatible with python3 and pypy

import urllib3
from pyquery import PyQuery as pyq

http = urllib3.PoolManager()
request = http.request('GET', 'http://acm.zju.edu.cn/onlinejudge/showProblemsets.do')
buffer = request.data

html = pyq(buffer)
print(html('#content_body > form:nth-child(1) > a:nth-child(10)').attr('href'))
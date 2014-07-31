#!/usr/bin/python3

# -*- Mode: Python; coding: utf-8; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*- 
#
# main.py
# Copyleft 2014 Yuzo(PillowSky) <Yuzo@pillowsky.org>
# Compatible with python3 and pypy
#
# require PyQuery which depend on cssselect, so I pack it in the project to ensure running normally on other computers

from Spider import Spider

spider = Spider()

#spider.fetchAllProblems()
print(spider.queryMatrixProblems())
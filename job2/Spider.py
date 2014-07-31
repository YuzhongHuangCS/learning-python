#!/usr/bin/python3

# -*- Mode: Python; coding: utf-8; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*- 
#
# main.py
# Copyleft 2014 Yuzo(PillowSky) <Yuzo@pillowsky.org>
# Compatible with python3 and pypy
#
# require PyQuery which depend on cssselect, so I pack it in the project to ensure running normally on other computers

from pyquery import PyQuery as pyq

class Spider(object):

	def __init__(self, arg = ''):
		super(Spider, self).__init__()
		self.arg = arg
		self.baseUrl = 'http://acm.zju.edu.cn'
		self.indexPath = '/onlinejudge/showProblemsets.do'
		self.voluemPath = '/onlinejudge/showProblems.do?contestId=1&pageNumber='
		self.problemPath = '/onlinejudge/showProblem.do?problemCode='

	def getVolumeCount(self):
		# d here have the same meaning with $ in jQuery
		d = pyq(url = self.baseUrl + self.indexPath)
		self.voluemCount = d('#content_body > form:nth-child(1) > a').length
		return self.voluemCount

	def getVoluemPathList(self):
		self.getVolumeCount()

		d = pyq(url = self.baseUrl + self.indexPath)
		return list(map(lambda i: d('#content_body > form:nth-child(1) > a:nth-child(%d)' % i).attr("href"), range(1, count+1)))

	def getProblemCount(self):
		self.getVolumeCount()
		
		d = pyq(url = self.baseUrl + self.voluemPath + str(self.voluemCount))
		self.problemCount = int(d('#content_body > form:nth-child(1) > table > tr:last-child > td.problemId > a > font').text())
		return self.problemCount

	def getProblemContent(self, id):
		d = pyq(url = self.baseUrl + self.problemPath + str(id))
		content = {
			"title": d('#content_body > center:nth-child(1) > span').text(),
			"body": d('#content_body').text()
		}
		return content


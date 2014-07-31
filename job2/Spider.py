#!/usr/bin/python3

# -*- Mode: Python; coding: utf-8; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*- 
#
# main.py
# Copyleft 2014 Yuzo(PillowSky) <Yuzo@pillowsky.org>
# Compatible with python3 and pypy
#
# require PyQuery which depend on cssselect, so I pack it in the project to ensure running normally on other computers

from pyquery import PyQuery as pyq
import sqlite3

class Spider(object):

	def __init__(self, arg = ''):
		super(Spider, self).__init__()
		# data member initialize
		self.arg = arg
		self.baseUrl = 'http://acm.zju.edu.cn'
		self.indexPath = '/onlinejudge/showProblemsets.do'
		self.voluemPath = '/onlinejudge/showProblems.do?contestId=1&pageNumber='
		self.problemPath = '/onlinejudge/showProblem.do?problemCode='

		#connect to db and checks
		self.db = sqlite3.connect("data.db", isolation_level = None)
		self.query = self.db.cursor()
		# use sqlite's FTS(Full Text Search) table to store the data and perform quick search
		self.query.execute("CREATE VIRTUAL TABLE IF NOT EXISTS problems USING fts4(id, title, body)")

	def getVolumeCount(self):
		# d here have the same meaning to $ in jQuery
		d = pyq(url = self.baseUrl + self.indexPath)
		self.voluemCount = d('#content_body > form:nth-child(1) > a').length
		return self.voluemCount

	def getVoluemPathList(self):
		# this function is deprecated
		# because the problemID is continuous 
		# and we don't have to access the problem from the voluem page
		# just use problemPath and problemCode to access the problem
		self.getVolumeCount()

		d = pyq(url = self.baseUrl + self.indexPath)
		return list(map(lambda i: d('#content_body > form:nth-child(1) > a:nth-child(%d)' % i).attr("href"), range(1, self.voluemCount+1)))

	def getProblemCount(self):
		self.getVolumeCount()
		
		d = pyq(url = self.baseUrl + self.voluemPath + str(self.voluemCount))
		self.problemCount = int(d('#content_body > form:nth-child(1) > table > tr:last-child > td.problemId > a > font').text())
		return self.problemCount

	def storeProblemContent(self, id):
		d = pyq(url = self.baseUrl + self.problemPath + str(id))
		content = {
			"title": d('#content_body > center:nth-child(1) > span').text(),
			"body": d('#content_body').text()
		}
		self.query.execute('INSERT INTO problems (id, title, body) VALUES (?, ?, ?)', (id, content['title'], content['body']))

	def fetchAllProblems(self):
		list(map(lambda i: self.storeProblemContent(i), range(1001, self.getProblemCount()+1)))

	def selectAllProblems(self):
		self.query.execute('SELECT COUNT(*) FROM problems')
		return(self.query.fetchall())

	def queryProblems(self, keyword):
		self.query.execute('SELECT id, title FROM problems WHERE body MATCH "%s"' % keyword)
		return(self.query.fetchall())

	def queryMatrixProblems(self):
		# use "simple" tokenizer by default in sqlite's FTS engine to lowercase the query string, so matrix and Matrix will get the same result 
		self.query.execute('SELECT id, title FROM problems WHERE body MATCH "%s" UNION SELECT id, title FROM problems WHERE body MATCH "%s"' % ("matrix", "matrices"))
		return(self.query.fetchall())
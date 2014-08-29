#!/usr/bin/python3

# -*- Mode: Python; coding: utf-8; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*- 
#
# main.py
# Copyleft 2014 Yuzo(PillowSky) <Yuzo@pillowsky.org>
# Compatible with python3 and pypy
#
# require PyQuery which depend on cssselect, so I pack it in the project to ensure running normally on other computers

from twisted.internet import epollreactor
epollreactor.install()
from twisted.internet import reactor
from twisted.web.client import Agent, HTTPConnectionPool, readBody
from twisted.internet.defer import DeferredSemaphore, gatherResults
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

	def getProblemMax(self):
		self.getVolumeCount()
		
		d = pyq(url = self.baseUrl + self.voluemPath + str(self.voluemCount))
		self.problemMax = int(d('#content_body > form:nth-child(1) > table > tr:last-child > td.problemId > a > font').text())
		self.problemCount = self.problemMax - 1001 + 1
		return self.problemMax

	def fetchProblem(self, id):
		d = pyq(url = self.baseUrl + self.problemPath + str(id))
		title = d('#content_body > center:nth-child(1) > span').text(),
		body = d('#content_body').text()
		print("Now fetching ProblemID: %s, Title: %s" % (id, title[0]))
		self.storeProblem(id, title[0], body)

	def storeProblem(self, id, title, body):
		# UPSERT in sqlite is INSERT OR REPLACE
		# rowid is a internal column in sqlite
		self.query.execute('INSERT OR REPLACE INTO problems (rowid, id, title, body) VALUES (?, ?, ?, ?)', (id-1000, id, title, body))

	def serialFetchAllProblems(self):
		self.query.execute('BEGIN')
		list(map(lambda i: self.fetchProblem(i), range(1001, self.getProblemMax()+1)))
		self.query.execute('COMMIT')

	def parallelFetchAllProblems(self):
			pool = HTTPConnectionPool(reactor)
			pool.maxPersistentPerHost = 10
			agent = Agent(reactor, pool=pool)
			sem = DeferredSemaphore(10)
			self.done = 0
			def assign():
				self.query.execute('BEGIN')
				for id in range(1001, self.getProblemMax()+1):
					sem.acquire().addCallback(requestFactory, id)
			
			def requestFactory(token, id):
				deferred = agent.request('GET', self.baseUrl + self.problemPath + str(id))
				deferred.addCallback(onHeader, id)
				deferred.addErrback(errorHandler, id)
				# sem lead to wait time in main loop, so needn't iterate manually
				# reactor.iterate(1)
				return deferred
			
			def onHeader(response, id):
				deferred = readBody(response)
				deferred.addCallback(onBody, id)
				deferred.addErrback(errorHandler, id)
				return deferred

			def onBody(html, id):
				sem.release()
				d = pyq(html)
				title = d('#content_body > center:nth-child(1) > span').text(),
				body = d('#content_body').text()
				print('Fetched ProblemID: %s, Title: %s, done: %s' % (id, title[0], self.done))
				self.storeProblem(id, title[0], body)
				self.done += 1
				if(self.done == self.problemCount):
					print('Fetch data used %s s' % (reactor.seconds() - startTimeStamp))
					print('Fetch data end, writing to database')
					self.query.execute('COMMIT')
					reactor.stop()

			def errorHandler(err, id):
				print('[%s] id %s: %s' % (reactor.seconds() - startTimeStamp, id, err))

			startTimeStamp = reactor.seconds()
			reactor.callWhenRunning(assign)
			reactor.run()

	def selectAllProblems(self):
		self.query.execute('SELECT * FROM problems')
		return(self.query.fetchall())

	def queryProblems(self, keyword):
		self.query.execute('SELECT id, title FROM problems WHERE body MATCH "%s"' % keyword)
		return(self.query.fetchall())

	def queryMatrixProblems(self):
		# use "simple" tokenizer by default in sqlite's FTS engine to lowercase the query string, so matrix and Matrix will get the same result
		# and use UNION in SQL to merge matrix and matrices's result
		self.query.execute('SELECT id, title FROM problems WHERE body MATCH "%s" UNION SELECT id, title FROM problems WHERE body MATCH "%s"' % ("matrix", "matrices"))
		return(self.query.fetchall())

	def getItemsCount(self):
		self.query.execute('SELECT COUNT(*) FROM problems')
		return(self.query.fetchone())

	def printProblems(self, problems):
		for i in problems:
			print("ProblemID: %s, Title: %s, Link: %s%s%s" % (i[0], i[1], self.baseUrl, self.problemPath, i[0]))
		print("%s problems match your keyword" % len(problems))
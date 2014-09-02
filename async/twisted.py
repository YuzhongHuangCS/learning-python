#!/usr/bin/env python
from twisted.internet import reactor
from twisted.web.client import Agent, HTTPConnectionPool, readBody
from twisted.internet.defer import DeferredSemaphore

baseUrl = 'http://acm.zju.edu.cn/onlinejudge/showProblem.do?problemCode='

start = 1001
end = 3800
count = end - start
concurrency = 10
pool = HTTPConnectionPool(reactor)
pool.maxPersistentPerHost = concurrency
agent = Agent(reactor, pool=pool)
sem = DeferredSemaphore(concurrency)
done = 0

def onHeader(response, i):
	deferred = readBody(response)
	deferred.addCallback(onBody, i)
	deferred.addErrback(errorHandler, i)
	return deferred

def onBody(body, i):
	sem.release()
	global done, count
	done += 1
	print('Received %s, Length %s, Done %s' % (i, len(body), done))
	if(done == count):
		print('All items fetched')
		reactor.stop()

def errorHandler(err, i):
	print('[%s] id %s: %s' % (reactor.seconds() - startTimeStamp, i, err))

def requestFactory(token, i):
	deferred = agent.request('GET', baseUrl + str(i))
	deferred.addCallback(onHeader, i)
	deferred.addErrback(errorHandler, i)
	print('Request send %s' % i)
	#this function it self is a callback emit by reactor, so needn't iterate manually
	#reactor.iterate(1)
	return deferred

def assign():
	for i in range (start, end):
		sem.acquire().addCallback(requestFactory, i)

startTimeStamp = reactor.seconds()
reactor.callWhenRunning(assign)
reactor.run()
#!/usr/bin/env python
from twisted.internet import epollreactor
epollreactor.install()
from twisted.internet import reactor
from twisted.web.client import Agent, HTTPConnectionPool, readBody
from twisted.internet.defer import DeferredSemaphore, gatherResults

baseUrl = 'http://acm.zju.edu.cn/onlinejudge/showProblem.do?problemCode='

start = 1001
end = 3500

pool = HTTPConnectionPool(reactor)
pool.maxPersistentPerHost = 10
agent = Agent(reactor, pool=pool)

done = 0

def onHeader(response, i):
	deferred = readBody(response)
	deferred.addCallback(onBody, i)
	deferred.addErrback(errorHandler, i)

	return deferred

def onBody(body, i):
	global done
	done += 1
	print(len(pool._connections[('http', 'acm.zju.edu.cn', 80)]))
	print('Received %s, Length %s, done %s' % (i, len(body), done))

def errorHandler(err, i):
	print('[%s] id %s: %s' % (reactor.seconds() - startTimeStamp, i, err))

def requestFactory(i):
	deferred = agent.request('GET', baseUrl + str(i))
	deferred.addCallback(onHeader, i)
	deferred.addErrback(errorHandler, i)
	print('Generated %s' % i)
	reactor.iterate(1)
	return deferred

sem = DeferredSemaphore(100)

def main():
	for i in range (start, end):
		sem.run(requestFactory, i)

startTimeStamp = reactor.seconds()
reactor.callWhenRunning(main)
reactor.run()
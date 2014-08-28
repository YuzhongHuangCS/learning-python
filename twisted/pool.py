#!/usr/bin/env python
from twisted.internet import epollreactor
epollreactor.install()
from twisted.internet import reactor
from twisted.web.client import Agent, HTTPConnectionPool, readBody

baseUrl = 'http://acm.zju.edu.cn/onlinejudge/showProblem.do?problemCode='

start = 1001
end = 3500

pool = HTTPConnectionPool(reactor)
pool.maxPersistentPerHost = 10
agent = Agent(reactor, pool=pool)

def onHeader(response, i):
    deferred = readBody(response)
    deferred.addCallback(onBody, i)
    deferred.addErrback(errorHandler)
    return response

def onBody(body, i):
    print('Received %s, Length %s' % (i, len(body)))

def errorHandler(err):
    print('%s : %s' % (reactor.seconds() - startTimeStamp, err))

def requestFactory():
    for i in range (start, end):
        deferred = agent.request('GET', baseUrl + str(i))
        deferred.addCallback(onHeader, i)
        deferred.addErrback(errorHandler)
        print('Generated %s' % i)
        reactor.iterate(1)
    
    print('All requests has generated, elpased %s' % (reactor.seconds() - startTimeStamp))

startTimeStamp = reactor.seconds()
reactor.callWhenRunning(requestFactory)
reactor.run()

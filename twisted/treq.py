#!/usr/bin/env python
from twisted.internet import epollreactor
epollreactor.install()
from twisted.internet import reactor
import treq

baseUrl = 'http://acm.zju.edu.cn/onlinejudge/showProblem.do?problemCode='

start = 1001
end = 3500

def onHeader(response, i): 
    deferred = treq.text_content(response)
    deferred.addCallback(onBody, i)
    deferred.addErrback(errorHandler)
    return response

def onBody(body, i):
    print('Received %s, Length %s' % (i, len(body)))

def errorHandler(err):
    print('%s : %s' % (reactor.seconds() - startTimeStamp, err))

def requestFactory():
    for i in range (start, end):
        deferred = treq.get(baseUrl + str(i))
        deferred.addCallback(onHeader, i)
        deferred.addErrback(errorHandler)
        print('Generated %s' % i)
        reactor.iterate(1)

    print('All requests has generated, elpased %s' % (reactor.seconds() - startTimeStamp))

startTimeStamp = reactor.seconds()
reactor.callWhenRunning(requestFactory)
reactor.run()
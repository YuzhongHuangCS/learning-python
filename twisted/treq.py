#!/usr/bin/env python
from twisted.internet import epollreactor
epollreactor
from twisted.internet import reactor, task
import treq

cooperator = task.Cooperator()
baseUrl = 'http://acm.zju.edu.cn/onlinejudge/showProblem.do?problemCode='

start = 1001
end = 3500

def onHeader(response, i):  
    deferred = treq.text_content(response)
    deferred.addCallback(onBody, i)
    deferred.addErrback(errorHandler)
    return deferred

def onBody(body, i):
    print('Received %s, Length %s' % (i, len(body)))

def errorHandler(err):
    print(err)

def requestFactory():  
    for i in range (start, end):
        print('Generated %s' % i)
        deferred = treq.get(baseUrl + str(i))
        deferred.addCallback(onHeader, i)
        deferred.addErrback(errorHandler)
        
        #reactor.iterate()
        #reactor.callLater(2,printTime)
        yield None

if __name__ == '__main__':  
    # make cooperator work on spawning requests
    cooperator.cooperate(requestFactory())
    
    #reactor.callWhenRunning(requestFactory)
    reactor.run()
#!/usr/bin/env python
from twisted.internet import epollreactor
epollreactor.install()
from twisted.internet import reactor, task
import treq

cooperator = task.Cooperator()
done = 0

baseUrl = 'http://acm.zju.edu.cn/onlinejudge/showProblem.do?problemCode='

def onHeader(response, i):  
    deferred = treq.text_content(response)
    deferred.addCallback(onBody, i)
    deferred.addErrback(errorHandler)
    return deferred

def onBody(body, i):
    global done
    done += 1
    print('Received %s, Length %s, done %s' % (i, len(body), done))

def errorHandler(err):
    global reactor
    print(err)
    reactor.stop()
    exit()

def requestFactory():  
    global baseUrl, reactor
    for i in range (1001, 3500):
        print('Generator %s' % i)
        deferred = treq.get(baseUrl + str(i))
        deferred.addCallback(onHeader, i)
        deferred.addErrback(errorHandler)
        reactor.iterate()
        #reactor.callLater(2,printTime)
        yield None

if __name__ == '__main__':  
    # make cooperator work on spawning requests
    cooperator.cooperate(requestFactory())
    
    #reactor.callWhenRunning(requestFactory)
    reactor.run()
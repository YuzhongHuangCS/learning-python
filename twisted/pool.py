from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredList
from twisted.internet.protocol import Protocol
from twisted.web.client import Agent, HTTPConnectionPool

baseUrl = 'http://acm.zju.edu.cn/onlinejudge/showProblem.do?problemCode='

start = 1001
upLimit = 3000
current = start

class onBody(Protocol):
    def __init__(self, deferred):
        self.deferred = deferred
        self.body = ''

    def dataReceived(self, bytes):
        self.body += bytes

    def connectionLost(self, reason):
        self._factory.pool.release(None)
        #print(reason)
        global current
        print('No. %s, HTML length: %s ' % (current, len(self.body)))
        current += 1
        
def onHeader(response):
    response.deliverBody(onBody(response))
    return response

def errorHandler(err):
    print(err)

def requestFactory():
    for i in range(start, upLimit):
        deferred = agent.request('GET', baseUrl + str(i))
        deferred.addCallback(onHeader)
        deferred.addErrback(errorHandler)
        reactor.iterate(1)

pool = HTTPConnectionPool(reactor)
#pool.maxPersistentPerHost = 5
agent = Agent(reactor, pool=pool)

reactor.callWhenRunning(requestFactory)
reactor.run()

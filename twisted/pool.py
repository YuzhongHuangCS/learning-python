import time
from twisted.internet import reactor, task
from twisted.internet.protocol import Protocol
from twisted.web.client import Agent, HTTPConnectionPool

baseUrl = 'http://acm.zju.edu.cn/onlinejudge/showProblem.do?problemCode='

start = 1001
upLimit = 3000

class onBody(Protocol):
    def __init__(self, deferred, i):
        self.deferred = deferred
        self.i = i
        self.body = ''

    def dataReceived(self, bytes):
        self.body += bytes

    def connectionLost(self, reason):
        if str(reason.value) == 'Response body fully received':
            print('No. %s, HTML length: %s ' % (self.i, len(self.body)))
        else:
            print(reason)
        
def onHeader(response, i):
    response.deliverBody(onBody(response, i))
    return response

def errorHandler(err):
    print(err)

def requestFactory():
    for i in range(start, upLimit):
        deferred = agent.request('GET', baseUrl + str(i))
        deferred.addCallback(onHeader, i)
        deferred.addErrback(errorHandler)
        print('Generated %s' % i)
        #reactor.iterate(1)
        yield None

    print(time.time() - startTimeStamp)
    yield True

pool = HTTPConnectionPool(reactor)
pool.maxPersistentPerHost = 5
agent = Agent(reactor, pool=pool)

startTimeStamp = time.time()
cooperator = task.Cooperator()
cooperator.cooperate(requestFactory())
#reactor.callWhenRunning(requestFactory)
reactor.run()

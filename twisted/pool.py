from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredList
from twisted.internet.protocol import Protocol
from twisted.web.client import Agent, HTTPConnectionPool

baseUrl = 'http://acm.zju.edu.cn/onlinejudge/showProblem.do?problemCode='

start = 1001
upLimit = 3500
current = start

class storeBody(Protocol):
    def __init__(self, deferred):
        self.deferred = deferred
        self.body = ''

    def dataReceived(self, bytes):
        self.body += bytes

    def connectionLost(self, reason):
        #print(reason)
        global current
        print('No. %s, HTML length: %s ' % (current, len(self.body)))
        current += 1

def cbRequest(response):
    response.deliverBody(storeBody(response))
    return response

def stop(ignored):
    reactor.stop()

pool = HTTPConnectionPool(reactor)
pool.maxPersistentPerHost = 10
agent = Agent(reactor, pool=pool)

for i in range(start, upLimit):
    d = agent.request('GET', baseUrl + str(i))
    d.addCallback(cbRequest)

reactor.run()

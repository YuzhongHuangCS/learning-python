from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol
from twisted.web.client import Agent, HTTPConnectionPool, readBody

def onHeader(response):
	#print(pool._connections)
	print 'Response code:', response.code
	deferred = readBody(response)
	deferred.addCallback(onBody)

	return deferred

def onBody(body):
	# print(pool._connections)
	print('Received, Length %s' % (len(body)))

pool = HTTPConnectionPool(reactor)
pool.maxPersistentPerHost = 10
agent = Agent(reactor, pool=pool)

def requestFactory():
	# print(pool._connections)
	for i in range(4):
		deferred = agent.request('GET', 'http://localhost/')
		deferred.addCallback(onHeader)
	reactor.callLater(1, requestFactory)

reactor.callWhenRunning(requestFactory)
reactor.run()
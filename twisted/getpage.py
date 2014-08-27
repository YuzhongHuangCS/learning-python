from twisted.internet import reactor
from twisted.web.client import getPage

baseUrl = 'http://acm.zju.edu.cn/onlinejudge/showProblem.do?problemCode='

start = 1001
upLimit = 2000
current = start

def callback(value):
	global current
	print('No.%s, length %s' % (current, len(value)))
	current += 1

def errback(error):
	print('Error' + error)

for i in range(start, upLimit):
	getPage(baseUrl + str(i)).addCallbacks(
    	callback = callback,
    	errback = errback
	)

reactor.run()

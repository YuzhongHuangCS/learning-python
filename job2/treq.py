from twisted.internet import epollreactor
epollreactor.install()
from twisted.internet import reactor
import treq

baseUrl = 'http://acm.zju.edu.cn/onlinejudge/showProblem.do?problemCode='

start = 1001
upLimit = 2000
current = 1001

def receive(response, id):
	return treq.text_content(response).addCallback(content, id)

def content(html, id):
	print('No. %s, HTML length %s' %(id, len(html)))
	global current
	current += 1
	print('Current:' + str(current))
	if(current == upLimit):
		reactor.stop()

def initTasks():
	for i in range(start, upLimit):
		print('Spawn' + str(i))
		treq.get(baseUrl + str(i), timeout=300).addCallback(receive, i)
		reactor.iterate(10)

reactor.callWhenRunning(initTasks)
reactor.run()
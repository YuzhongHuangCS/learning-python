import treq
from twisted.internet import reactor

baseUrl = 'http://acm.zju.edu.cn/onlinejudge/showProblem.do?problemCode='

start = 1001
upLimit = 3500
current = start

def done(response):
	return treq.text_content(response).addCallback(content)

def content(html):
	global current
	print('No. %s, HTML length %s' %(current, len(html)))
	current += 1
	#reactor.stop()

for i in range(start, upLimit):
	treq.get(baseUrl + str(i)).addCallback(done)

reactor.run()
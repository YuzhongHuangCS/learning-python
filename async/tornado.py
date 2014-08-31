#!/usr/bin/env python
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.ioloop import IOLoop

baseUrl = 'http://acm.zju.edu.cn/onlinejudge/showProblem.do?problemCode='

start = 1001
end = 3800
count = end - start
done = 0

client = AsyncHTTPClient()

def onResponse(response):
	if response.error:
		print('Error: %s' % response.error)
	else:
		global done
		done += 1
		#It is comment out here, you could uncomment it and watch something interest, that len(client.queue) is reduce 10 by 10.
		#print('Queue length %s, Active client count %s, Max active clients limit %s' % (len(client.queue), len(client.active), client.max_clients))
		print('Received %s, Content length %s, Done %s' % (response.effective_url[-4:], len(response.body), done))
		if(done == count):
			IOLoop.instance().stop()

for i in range (start, end):
	request = HTTPRequest(baseUrl + str(i), connect_timeout=float('inf'), request_timeout=float('inf'))
	client.fetch(request, onResponse)
	print('Generated %s' % i)

IOLoop.instance().start()
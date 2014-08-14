#!/usr/bin/python3

# -*- Mode: Python; coding: utf-8; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*- 
#
import urllib
import urllib2
import requests
from cookielib import CookieJar
from pyquery import PyQuery as pyq

import sys  
reload(sys)  
sys.setdefaultencoding('utf-8')

'''
fields = {
	'followup': '199052809',
	'RootID': '4223610',
	'star': '1',
	'Expression': 'face7.gif',
	'Content': 'wah',
	'signflag': 'yes'
}

headers = {
	'Referer': 'http://www.cc98.org/dispbbs.asp?BoardID=509&id=4223610',
	'Cookie': 'aspsky=username=hyz98&usercookies=3&userhidden=2&password=b3fb351bc84484fd&userid=433480&useranony=; BoardList=BoardID=Show; owaenabled=True; autoplay=True; ASPSESSIONIDQSDSADQC=OBEAMKMBFMAMFNINPJGOMPAG; upNum=0',
}

#r = urllib2.request('POST', 'http://www.idi.zju.edu.cn/echo.php', fields, headers)
#r = urllib2.urlopen('http://www.cc98.org/SaveReAnnounce.asp?method=fastreply&BoardID=509', urllib.urlencode(fields), headers)
#r = urllib2.urlopen('http://www.idi.zju.edu.cn/echo.php', urllib.urlencode(fields), headers)
#req = urllib2.Request('http://www.cc98.org/SaveReAnnounce.asp?method=fastreply&BoardID=509', urllib.urlencode(fields), headers)
#res = urllib2.urlopen(req)
#print (res.read())

username = "hyz98"
password = "huan9hu1"

info = {"username" : "hyz98", "password" : "huan9hu1", "action" : "chk"}
#result = opener.open(loginUrl, urllib.urlencode(info))
#result.read()


#cookie = CookieJar()
#opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
#page = opener.open("http://www.cc98.org/dispbbs.asp?boardID=509&ID=4223610&page=1").read()
#d = pyq(page)
#print(d('#topicPagesNavigation > b').text())
#print(cookie)
#print d('body > table:nth-child(40) > tbody > tr > td:nth-child(1) > b').html()
'''

class ClassName(object):
	"""docstring for ClassName"""
	def __init__(self, arg):
		super(ClassName, self).__init__()
		self.arg = arg
		
class Replyer(object):
	def __init__(self, username, password):
		super(Replyer, self).__init__()
		self.loginUrl = 'http://www.cc98.org/login.asp'
		self.replyUrl = 'http://www.cc98.org/SaveReAnnounce.asp'
		self.cookie = CookieJar()
		self.opener = urllib2.build_opener()
		postData ={
			"username": username,
			"password": password,
			"action": "chk"
		}
		data = self.opener.open(self.loginUrl, urllib.urlencode({
			"username": username,
			"password": password,
			"action": "chk"
		}))
		r = requests.post(self.loginUrl, data=postData)
		print(r.content)
		self.cookie.extract_cookies(data, urllib2.Request('http://www.cc98.org/'))
		cookieContent = ''
		#due to buggy Set-cookie header and buggy python, I have to handle this myself
		for item in self.cookie:
			cookieContent += "%s=%s; " % (item.name, item.value)
		self.opener.addheaders = [('Cookie', cookieContent)]

	def info(self, url):
		html = self.opener.open(url).read()

		#print(html)
		# d here have the same meaning to $ in jQuery
		#keys = ('RootID', 'followup', 'UserName', 'passwd', 'star', 'signflag')
		#result = {key: soup.find(attrs={'name': key})['value'] for key in keys}
		d = pyq(html)
		#pyQuery can't handle buggy cc98's html document
		#print ("pyQuery")
		print d('[type="hidden"]').length
		#print(result)

foo = Replyer("hyz98", "huan9hu1")
foo.info("http://www.cc98.org/dispbbs.asp?BoardID=509&id=4223610")
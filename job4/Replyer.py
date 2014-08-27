#!/usr/bin/python3

# -*- Mode: Python; coding: utf-8; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*- 
#
# Replyer.py
# Copyleft 2014 Yuzo(PillowSky) <Yuzo@pillowsky.org>
# Compatible with python3 and pypy
#
# Depends: hashlib, requests, urlparse, pyquery
# Use requests library to get ride of ugly urllib/urllib2 apis and buggy CookieJar

import hashlib
import requests
import urlparse
from pyquery import PyQuery as pyq

class Replyer(object):
	def __init__(self, username, password):
		super(Replyer, self).__init__()
		self.loginUrl = 'http://www.cc98.org/login.asp'
		self.replyUrl = 'http://www.cc98.org/SaveReAnnounce.asp'
		postData ={
			"username": username,
			"password": password,
			"action": "chk"
		}

		# perform post action and raise exception if necessary
		r = requests.post(self.loginUrl, data=postData)
		r.raise_for_status()

		# extract and store cookies manually
		self.cookieData = dict()
		for item in r.cookies:
			self.cookieData[item.name] = item.value

	def reply(self, url, id):
		# perform get and pass the result to pyq
		r = requests.get(url, cookies=self.cookieData)
		r.raise_for_status()
		d = pyq(r.text)

		# setup needed fields and store their value into postData
		fields = ('RootID', 'followup', 'star')
		postData = dict()
		for item in fields:
			postData[item] = d('[name="' + item +'"]').attr('value')

		# fetch the reply floor using css selector
		floor = int(d('#topicPagesNavigation > b').text()) + 1
		postData['Content'] = "%s %s" % (floor, hashlib.sha1(id).hexdigest())
		postData['signflag'] = 'yes'
		postData['Expression'] = 'face7.gif'

		# add necessary referer header
		headers = {
			'Referer': 'http://www.cc98.org'
		}
		# parse and add query params
		params = {
			'method': 'fastreply'
		}
		queryStr=urlparse.parse_qs(urlparse.urlparse(url).query)
		params['BoardID'] = queryStr['BoardID'][0]

		r = requests.post(self.replyUrl, params = params, headers=headers, cookies=self.cookieData, data=postData)
		r.raise_for_status()
		return (floor, postData['Content'])

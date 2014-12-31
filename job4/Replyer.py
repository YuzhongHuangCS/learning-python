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
from urllib import parse
from pyquery import PyQuery as pyq

class Replyer(object):
	loginUrl = 'http://www.cc98.org/login.asp'
	replyUrl = 'http://www.cc98.org/SaveReAnnounce.asp'
	postUrl = 'http://www.cc98.org/SaveAnnounce.asp'

	def __init__(self, username, password):
		super(Replyer, self).__init__()

		postData ={
			"username": username,
			"password": password,
			"action": "chk"
		}

		# perform post action and raise exception if necessary
		r = requests.post(self.loginUrl, data=postData)
		r.raise_for_status()

		if '登录成功' not in r.text:
			raise Exception('Login Failed')

		# extract and store cookies manually
		self.cookieData = {}
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
		postData['Content'] = '%s %s' % (floor, hashlib.sha1(id.encode()).hexdigest())
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
		queryStr=parse.parse_qs(parse.urlparse(url).query)
		params['BoardID'] = queryStr['BoardID'][0]

		r = requests.post(self.replyUrl, params = params, headers=headers, cookies=self.cookieData, data=postData)
		r.raise_for_status()

		if '回复帖子成功' not in r.text:
			raise Exception('Reply Failed')

		return (floor, postData['Content'])

	def post(self, boardID, subject, content):
		token = {}

		for item in self.cookieData['aspsky'].split('&'):
			key, value = item.split('=')
			token[key] = value

		# add necessary referer header
		headers = {
			'Referer': 'http://www.cc98.org'
		}
		# parse and add query params
		params = {
			'boardID': boardID
		}

		postData = {
			"upfilerename": "",
			"username": token['username'],
			"passwd": token['password'],
			"subject": subject,
			"Expression": "face7.gif",
			"Content": content,
			"signflag": "yes"
		}

		r = requests.post(self.postUrl, params = params, headers=headers, cookies=self.cookieData, data=postData)
		r.raise_for_status()

		if '发表帖子成功' not in r.text:
			raise Exception('Post Failed')

		return boardID

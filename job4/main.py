#!/usr/bin/python3

# -*- Mode: Python; coding: utf-8; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*- 
#
# main.py
# Copyleft 2014 Yuzo(PillowSky) <Yuzo@pillowsky.org>
# Compatible with python3 and pypy
#
# Depends: hashlib, requests, urlparse, pyquery
# Use requests library to get ride of ugly urllib/urllib2 apis and buggy CookieJar

from Replyer import Replyer

# I assume the first line in passwd.txt is username,
# and the second line is password.
# Both lines didn't have other content
try:
	f = open('passwd.txt')
	username = f.readline().strip('\n')
	password = f.readline().strip('\n')
	f.close()

except IOError as e:
	print("A passwd.txt file is required to get the program work")
	exit()

# hard code id to 3120102663, so do reply url
id = '3120102663'
url = 'http://www.cc98.org/dispbbs.asp?BoardID=509&id=4223610'

try:
	robot = Replyer(username, password)
	result = robot.reply(url, id)
	print('Successfully leave a reply on floor %s, content %s' % (result[0], result[1]))

except Exception as e:
	print("Error occured! " + str(e))
	exit()
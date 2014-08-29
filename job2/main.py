#!/usr/bin/python3

# -*- Mode: Python; coding: utf-8; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*- 
#
# main.py
# Copyleft 2014 Yuzo(PillowSky) <Yuzo@pillowsky.org>
# Compatible with python3 and pypy
#
# require PyQuery which depend on cssselect, so I pack it in the project to ensure running normally on other computers

import os.path
from datetime import datetime
from Spider import Spider

print("==Welcome to search engine for ZOJ==")
if(os.path.isfile("data.db")):
	spider = Spider()
	print("Local database is update on %s" % datetime.fromtimestamp(os.path.getmtime("data.db")))
	print("Database have %s problems stored now" % spider.getItemsCount())
else:
	print("Local database hasn't build")
	spider = Spider()

print("\nUsage:")
print("[1] update the local database in serial")
print("[2] update the local database in parallel")
print("[3] search problems about Matrix")
print("[4] search generic problems")
	
choice = raw_input()
if(choice == str(1)) :
	spider.serialFetchAllProblems()
else:
	if(choice == str(2)):
		spider.parallelFetchAllProblems()
	else:
		if(choice == str(3)):
			spider.printProblems(spider.queryMatrixProblems())
		else:
			if(choice == str(4)):
				keyword = input('Please enter the keyword: ')
				spider.printProblems(spider.queryProblems(keyword))
			else:
				print(">_< You typed something silly, byebye")
				exit()

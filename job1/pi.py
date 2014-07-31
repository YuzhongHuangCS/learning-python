#!/usr/bin/python3

# -*- Mode: Python; coding: utf-8; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*- 
#
# pi.py
# Copyleft 2014 Yuzo(PillowSky) <Yuzo@pillowsky.org>
# Compatible with python3 and pypy
import time; 

sum = 0.0
denominator = 1.0
numerator = 1.0

exponent = int(input('Please enter the exponent of the cycles (10^x) : '))
cycles = 10**exponent
#calc the print point
points = list(map(lambda i: 10**i, range(exponent+1)))

startTimeStamp = time.time()

#since python3, range behave like xrange in python2
for i in range(cycles+1) :
	sum += numerator / denominator
	numerator = -numerator
	denominator += 2
	if(i in points) :
		print("Calc 10^%s times, Pi = %s, Elapsed: %ss" % (points.index(i), sum*4, time.time() - startTimeStamp))
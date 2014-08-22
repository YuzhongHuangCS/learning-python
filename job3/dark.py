#!/usr/bin/ipython

# -*- Mode: Python; coding: utf-8; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*- 
#
# main.py
# Copyleft 2014 Yuzo(PillowSky) <Yuzo@pillowsky.org>
# Compatible with ipython
#
# require PIL as image process module, and IPython as display interface

import time
import heapq
from io import BytesIO
from PIL import Image
from IPython import display as disp

def memoed(fn):
	memo = {}
	def inner(*args):
		if args not in memo:
			memo[args] = fn(*args)
		return memo[args]
	return inner

def show(img):
	b = BytesIO()
	img.save(b, format='png')
	disp.display(disp.Image(data=b.getvalue(), format='png', embed=True))

def save(img):
	fp = open("darkmaze_output.png", 'w')
	img.save(fp, format='png')

def dark(point):
	# if any point within 7 * 7 area around the point is dark, that is considered very hard
	# although yeild is widely used in python, it's better return True once find a match point
	for ox in range(-3, 4):
		for oy in range(-3, 4):
			x, y = point
			if darkmaze.getpixel((x + ox, y + oy)) == (0, 0, 0):
				return True
	return False

@memoed
def cost(point):
	# palaces without lights really struggling
	return 1000 if dark(point) else 1

def forbidden(point):
	x, y = point
	#img.getpixel(point) == 0 means it is a black point
	return img.getpixel(point) == 0 or x < left or x > right or y < top or y > bottom

# entrance, data initialize
startTimeStamp = time.time()
darkmaze = Image.open('darkmaze.jpg')
img = darkmaze.convert('L').point(lambda x: 0 if x < 200 else 1, '1')

# define the edge points
start = (402, 984)
end = (398, 24)
top, right, bottom, left = 22, 793, 986, 7

# closed means visited
# note that dict in python is implemented with hashmap, so use dict to check exist is much faster
closed = {}
# d means distance
d = {
	start: 0
}
prev = {
	start: None
}
next = []
heapq.heappush(next, (d[start], start))

# main loop
while next:
	# use heap(priority queue) to get the closest point
	source = heapq.heappop(next)[1]
	if source == end:
		break
	if source in closed:
		continue
	closed[source] = 1
	for ox, oy in ((0, 1), (1, 0), (0, -1), (-1, 0)):
		x, y = source
		target = (x + ox, y + oy)
		if not forbidden(target) and target not in closed:
			if d[source] + cost(target) < d.get(target, float('inf')):
				d[target] = d[source] + cost(target)
				prev[target] = source
				heapq.heappush(next, (d[target], target))

#generate the path in reverse
path = []
p = end

while p != None:
	path.append(p)
	p = prev[p]

path.reverse()

out = darkmaze.point(lambda p: p / 2)
list(map(lambda p: out.putpixel(p, (255, 255, 255)), path))

save(out)
show(out)
print('Length of path: %s' % len(path))
print('Elapsed: %s s' % (time.time() - startTimeStamp))
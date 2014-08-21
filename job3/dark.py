from PIL import Image
from IPython import display as disp
from io import BytesIO
import heapq

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
	
darkmaze = Image.open('darkmaze.jpg')
# show(darkmaze)
img = darkmaze.convert('L').point(lambda x: 0 if x < 200 else 1, '1')
# show(img)
# mark the edge points
start = (402, 984)
end = (398, 24)
top, right, bottom, left = 22, 793, 986, 7

def dark(point):
    '''if any point within 7 * 7 area around the point is dark, that is considered without light'''
    def inner():
        for ox in range(-3, 4):
            for oy in range(-3, 4):
                x, y = point
                yield darkmaze.getpixel((x + ox, y + oy)) == (0, 0, 0)
    return max(inner())

@memoed
def cost(point):
    '''palaces without lights really struggling...'''
    return 1000 if dark(point) else 1

def forbidden(point):
	x, y = point
	#img.getpixel(point) == 0 means it is a black point
	return x < left or y < top or x > right or y > bottom or img.getpixel(point) == 0
	
prev = {start: None}
next = []
heapq.heappush(next, (0, start))
# closed means visited
# note that dict in python is implemented with hashmap, so use a dict rather than list
closed = {}
d = {start: 0}
while next:
	# choose a closest point (find index first)
    #index = min(range(len(next)), key=lambda i: d[next[i]])
    #source = next.pop(index)
    source = heapq.heappop(next)[1]
    if source == end:
        break
    if source in closed:
        continue
    closed[source] = 1
    print(len(closed))
    for ox, oy in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        x, y = source
        target = (x + ox, y + oy)
        if not forbidden(target) and target not in closed:
            if d[source] + cost(target) < d.get(target, float('inf')):
                d[target] = d[source] + cost(target)
                prev[target] = source
                #next.append(target)
                heapq.heappush(next, (d[target], target))
		
path = []
p = end
#generate the path in reverse
while p in prev:
	path.append(p)
	p = prev[p]
	
path = list(reversed(path))

print(len(path))

out = darkmaze.point(lambda p: p / 2)

for p in path:
    out.putpixel(p, (255, 255, 255))

show(out)
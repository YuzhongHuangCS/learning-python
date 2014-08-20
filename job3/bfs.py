from PIL import Image
from IPython import display as disp
from io import BytesIO
	
def show(img):
	b = BytesIO()
	img.save(b, format='png')
	disp.display(disp.Image(data=b.getvalue(), format='png', embed=True))
	
maze = Image.open('maze.jpg')
#show(maze)
img = maze.convert('L').point(lambda x: 0 if x < 200 else 1, '1')
#show(img)
#mark the edge points
start = (402, 984)
end = (398, 24)
top, right, bottom, left = 22, 793, 986, 7

def forbidden(point):
	x, y = point
	#img.getpixel(point) == 0 means it is a black point
	return x < left or y < top or x > right or y > bottom or img.getpixel(point) == 0
	
prev = {
	start: None
}
next = [start]
while next:
	# from stack to quene
	source = next.pop(0)
	if(forbidden(source)):
		continue
	if(source == end):
		break
	for ox, oy in ((0, 1), (1, 0), (0, -1), (-1, 0)): 
		x, y = source
		target = (x + ox, y + oy)
		# if the trial point has't be visited, push into the visit quene
		# note that one source point could match serveral target point
		if(target not in prev):
			prev[target] = source
			next.append(target)
		
path = []
p = end
#generate the path in reverse
while p in prev:
	path.append(p)
	p = prev[p]
	
path = list(reversed(path))
print(len(path))

out = maze.point(lambda p: p / 2)

for p in path:
    out.putpixel(p, (255, 255, 255))

show(out)
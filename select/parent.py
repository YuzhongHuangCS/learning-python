import os, select
import selectors
print('parent')
os.mkfifo('/tmp/tid_1')

fd = os.open('/tmp/tid_1', os.O_NONBLOCK | os.O_RDONLY)

sel = selectors.DefaultSelector()
sel.register(fd, selectors.EVENT_READ)

while True:
	print('Loop')
	events = sel.select()
	print('Event happen')
	print(events)

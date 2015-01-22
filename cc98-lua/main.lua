json = require 'luci.json'
Replyer = require 'Replyer'

fd = io.open('zombie.json', 'r')
if not fd then
	print('Require zombie.json to run the program.')
	return 1
else
	data = json.decode(fd:read("*a"))
end

count = 0
for k, v in pairs(data) do
	count = count + 1
end

math.randomseed(os.time())
want = math.random(1, count)

k, v = nil, nil
for i = 1, want do
	k, v = next(data, k)
end

robot = Replyer:new(k, v)
if not robot then
	print(string.format("Failed to login as %s:%s", k, v))
	return -1
else
	print(string.format("Successfully login as %s", k))
end

boardID, subject = robot:post(499, 'title', 'body')
if not boardID then
	print('Post Thread Failed')
	return -1
else
	print(string.format("Successfully post a thread on board %s, subject %s", boardID, subject))
end

boardID, rootID, content = robot:reply(509, 4223610, 'LuCI httpclient 0.1')
if not boardID then
	print('Reply Thread Failed')
	return -1
else
	print(string.format("Successfully leave a reply on board %s, thread %s, content %s", boardID, rootID, content))
end

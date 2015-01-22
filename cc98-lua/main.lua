json = require 'luci.json'
Replyer = require 'Replyer'

fd = io.open('zombie.json', 'r')
if not fd then
	print('Require zombie.json to run the program.')
	return 1
else
	data = json.decode(fd:read())
end

robot = Replyer:new(pairs(data)(data))
if not robot then
	print('Login Failed')
	return -1
end

result = robot:post(509, 'title', 'body')
if not result then
	print('Post Thread Failed')
	return -1
else
	print(string.format("Successfully post a thread on board %s", result))
end

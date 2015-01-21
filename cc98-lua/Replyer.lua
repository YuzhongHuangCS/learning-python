http = require 'luci.http.protocol'
client = require 'luci.httpclient'

Replyer = {
	loginUrl = 'http://www.cc98.org/login.asp',
	replyUrl = 'http://www.cc98.org/SaveReAnnounce.asp',
	postUrl = 'http://www.cc98.org/SaveAnnounce.asp'
}
Replyer.__index = Replyer

function Replyer:new(username, password)
	postData = {
		username = username,
		password = password,
		action =  'chk'
	}
	code, response, body, sock = client.request_raw(self.loginUrl, {body = postData})

	body = body..sock:readall()
	if not body:find('登录成功') then
		return nil
	end

	return setmetatable({cookies = response.cookies}, Replyer)
end

function Replyer:post(boardID, subject, content)
	token = {}
	encodedCookie = ''
	for _, c in pairs(self.cookies) do
		encodedCookie = encodedCookie .. c.key .. "=" .. c.value .. "; "
		if c.key == 'aspsky' then
			base = c.value
		end
	end
	for k, v in string.gmatch(base, '(%w+)=(%w+)') do
		token[k] = v
	end

	-- add necessary referer header, parse and add query params
	-- cookies must add manually, built-in implementation add cookie one by one
	options = {
		headers = {
			Referer = 'http://www.cc98.org',
			Cookie = encodedCookie
		},
		body = {
			upfilerename = '',
			username = token['username'],
			passwd = token['password'],
			subject = subject,
			Expression = 'face7.gif',
			Content = content,
			signflag = 'yes'
		}
	}

	url = self.postUrl .. '?' .. http.urlencode_params({boardID = boardID})
	code, response, body, sock = client.request_raw(url, options)
	body = body..sock:readall()

	if not body:find('发表帖子成功') then
		return nil
	else
		return boardID
	end
end

return Replyer

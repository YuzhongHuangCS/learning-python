-- Note: This file require a patched version of "luci.httpclient"
-- https://github.com/Preffer/luci

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
	code, response, body = client.request_raw(self.loginUrl, {body = postData})

	if not body:find('登录成功') then
		return nil
	else
		for _, c in ipairs(response.cookies) do
			c.flags.path = '/'
		end
		return setmetatable({cookies = response.cookies}, Replyer)
	end
end

function Replyer:post(boardID, subject, content)
	token = {}
	for _, c in ipairs(self.cookies) do
		if c.key == 'aspsky' then
			base = c.value
			break
		end
	end
	for k, v in string.gmatch(base, '(%w+)=(%w+)') do
		token[k] = v
	end

	options = {
		cookies = self.cookies,
		params = {
			boardID = boardID
		},
		headers = {
			Referer = 'http://www.cc98.org'
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

	code, response, body = client.request_raw(self.postUrl, options)

	if not body:find('发表帖子成功') then
		return nil
	else
		return boardID, subject
	end
end

function Replyer:reply(boardID, rootID, content)
	options = {
		cookies = self.cookies,
		params = {
			BoardID = boardID,
			method = 'fastreply'
		},
		headers = {
			Referer = 'http://www.cc98.org'
		},
		body = {
			RootID = rootID,
			followup = rootID,
			star = 1,
			Content = content,
			signflag = 'yes',
			Expression = 'face7.gif'
		}
	}

	code, response, body = client.request_raw(self.replyUrl, options)

	if not body:find('回复帖子成功') then
		return nil
	else
		return boardID, rootID, content
	end
end

return Replyer

'use strict'
fs = require 'fs'
engine = require './Spider'

process.on 'uncaughtException', (err) ->
	console.log err

console.log '==Welcome to search engine for ZOJ=='

if fs.existsSync 'data.db'
	console.log 'Local database is update on ' + fs.statSync('data.db').mtime
	Spider = new engine.Spider()
	Spider.getItemCount()
else
	console.log "Local database hasn't build"
	Spider = new engine.Spider()

console.log 'Usage:'
console.log '[1] update the local database in single process'
console.log '[2] update the local database in multi process'
console.log '[3] search problems'

# process.stdin.resume()
running = false;
search = false;

process.stdin.setEncoding 'utf8'
process.stdin.on 'data', (chunk)->
	if !running
		# remove the \n manually
		chunk = chunk.replace '\n', ''
		switch chunk
			when '1'
				Spider.run()
				running = true
			when '2'
				Spider.run 'parallel'
				running = true
			when '3'
				console.log 'Please enter the keyword: '
				search = true
			else
				if search
					Spider.queryProblems(chunk);
					running = true;
				else
					console.log('>_< You typed something silly, byebye');
					process.exit(0);
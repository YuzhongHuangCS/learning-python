'use strict'
http = require 'http'

req_generated = req_made = req_done = 0
url = 'http://localhost:8080'

request = ->
	req_generated++
	req = http.get url, (res) ->
		req_made++
		
		res.on 'end', ->
			req_done++

	req.on 'error', (e) ->
			console.log "problem with request: #{e.message}"

	setImmediate request

counter = ->
	console.log("Requests: #{req_generated} generated; #{req_made} made; #{req_done} done")
	req_generated = req_made = req_done = 0
	setTimeout counter, 1000

setTimeout counter, 1000
request()
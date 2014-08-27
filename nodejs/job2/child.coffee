'use strict'
jsdom = require 'jsdom'

process.on 'uncaughtException', (err) ->
	console.log err

process.on 'message', (m) ->
	id = m[0]
	html = m[1]
	jsdom.env html, (errors, window) ->
		$ = require('jquery')(window)
		title = $('#content_body > center:nth-child(1) > span').text()
		body = $('#content_body').text()
		console.log 'Parsed ProblemID: ' + id + ', Title: ' + title
		process.send([id, title, body]);
		window.close()

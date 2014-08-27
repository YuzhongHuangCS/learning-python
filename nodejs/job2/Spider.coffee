'use strict'
http = require 'http'
jsdom = require 'jsdom'
sqlite3 = require 'sqlite3'
child_process = require 'child_process'
numCPUs = require('os').cpus().length

class Spider
	constructor: ->
		# prepare database
		# use sqlite's FTS(Full Text Search) table to store the data and perform quick search
		@db = new sqlite3.Database('data.db')
		@db.run 'CREATE VIRTUAL TABLE IF NOT EXISTS problems USING fts4(id, title, body)'
		# define config
		@baseUrl = 'http://acm.zju.edu.cn'
		@indexPath = '/onlinejudge/showProblemsets.do'
		@voluemPath = '/onlinejudge/showProblems.do?contestId=1&pageNumber='
		@problemPath = '/onlinejudge/showProblem.do?problemCode='
		@problemMin = 1001

	# define function
	run: (mode) =>
		@mode = mode
		@getVolumeCount()

	getVolumeCount: =>
		jsdom.env
			url: @baseUrl + @indexPath
			done: (errors, window) =>
				@voluemCount = window.document.querySelectorAll('#content_body > form:nth-child(1) > a').length
				
				# console.log @voluemCount
				window.close()
				@getProblemMax()

	###
	this function is deprecated
	because the problemID is continuous 
	and we don't have to access the problem from the voluem page
	just use problemPath and problemCode to access the problem
	###
	getVoluemPathList: =>
		jsdom.env
			url: @baseUrl + @indexPath
			done: (errors, window) =>
				@voluemPathList = window.document.querySelectorAll('#content_body > form:nth-child(1) > a')._toArray().map (item) ->
					return item.getAttribute 'href'
				
				# console.log @voluemPathList
				window.close()

	getProblemMax: =>
		jsdom.env
			url: @baseUrl + @voluemPath + @voluemCount
			done: (errors, window) =>
				$ = require('jquery')(window)
				@problemMax = $('#content_body > form:nth-child(1) > table > tr:last-child > td.problemId > a > font').text()
				@problemCount = @problemMax - @problemMin + 1
				console.log "#{@problemCount} Problems in total"
				window.close()
				if @mode == 'parallel' then @parallelFetchAllProblems() else @serializeFetchAllProblems()

	fetchStoreProblem: (id) =>
		jsdom.env
			url: @baseUrl + @problemPath + id
			done: (errors, window) =>
				$ = require('jquery')(window)
				title = $('#content_body > center:nth-child(1) > span').text()
				body = $('#content_body').text()
				console.log "Now fetching ProblemID: #{id}, Title: #{title}"
				@stmt.run(id - @problemMin, id, title, body)
				@done++
				window.close()
				@afterFetch() if @done == @problemCount

	prepareFetch: =>
		@db.serialize =>
			# UPSERT in sqlite is INSERT OR REPLACE
			# rowid is a internal column in sqlite
			@stmt = @db.prepare('INSERT OR REPLACE INTO problems (rowid, id, title, body) VALUES (?, ?, ?, ?)')
			@db.run('BEGIN')

		@tpstart = Date.now()
		@done = 0

	afterFetch: =>
		@tpend = Date.now()
		console.log "Fetch data used #{(@tpend - @tpstart)/1000} s"
					
		console.log 'Fetch data end, writing to database'
		@tpstart = Date.now()
		@db.serialize =>
			@db.run('COMMIT')
			@stmt.finalize()

		@db.close =>
			@tpend = Date.now()
			console.log "Wirte to database used #{(@tpend - @tpstart)/1000} s"
			@exit()

	serializeFetchAllProblems: =>
		@prepareFetch()
		for i in [@problemMin...@problemMax]
			@fetchStoreProblem(i)

	fetchProblem: (id) =>
		# this request may take long time, so use native http.client to handle it
		url = @baseUrl + @problemPath + id
		req = http.get url, (res) =>
			body = ''
			res.on 'data', (chunk) =>
				body += chunk

			res.on 'end', =>
				console.log "Fetched ProblemID: #{id}"
				@child[id % numCPUs].send([id, body])

		req.on 'error', (e) ->
			console.log "problem with request: #{e.message}"

	storeProblem: (id, title, body) =>
		@stmt.run(id - @problemMin, id, title, body)
		@done++
		@afterFetch() if @done == @problemCount

	parallelFetchAllProblems: =>
		@prepareFetch()
		# fork child process to parse the html
		@child = []

		for i in [0...numCPUs]
			@child[i] = child_process.fork('./child.js')
			@child[i].on 'message', (m)=>
				@storeProblem(m[0], m[1], m[2])

		# map the burden
		for i in [@problemMin...@problemMax]
			@fetchProblem(i)

	selectAllProblems: =>
		@db.each 'SELECT * FROM problems', (err, row) ->
			console.log(row)

	queryProblems: (keyword) =>
		@db.each 'SELECT id, title FROM problems WHERE body MATCH ?', keyword
		, (err, row) =>
			console.log "ProblemID: #{row.id}, Title: #{row.title}, Link: #{@baseUrl + @problemPath + row.id}"
		
		, (err, count) =>
			console.log "#{count} problems match your keyword"
			@exit()

	getItemCount: =>
		@db.get 'SELECT COUNT(*) AS count FROM problems'
		, (error, row)->
			console.log "Database have #{row.count} problems stored now"

	exit: ->
		process.exit(0)

exports.Spider = Spider;
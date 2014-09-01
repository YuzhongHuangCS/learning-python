'use strict'
http = require 'http'
cheerio = require 'cheerio'
sqlite3 = require 'sqlite3'

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
	run: =>
		@getVolumeCount()

	fetch: (url, callback) =>
		req = http.get url, (res) =>
			body = ''
			res.on 'data', (chunk) =>
				body += chunk

			res.on 'end', =>
				callback body

		req.on 'error', (e) =>
			console.log "Problem with request #{url}: #{e.message}"
			@fetch(url, callback)

	getVolumeCount: =>
		@fetch @baseUrl + @indexPath, (body) =>
			$ = cheerio.load(body)
			@voluemCount = $('#content_body > form:nth-child(1) > a').length
			# console.log @voluemCount
			@getProblemMax()

	getProblemMax: =>
		@fetch @baseUrl + @voluemPath + @voluemCount, (body) =>
			$ = cheerio.load(body)
			@problemMax = $('#content_body > form:nth-child(1) > table > tr:last-child > td.problemId > a > font').text()
			@problemCount = @problemMax - @problemMin + 1
			console.log "#{@problemCount} Problems in total"
			@fetchAllProblems()

	prepareFetch: =>
		@db.serialize =>
			# UPSERT in sqlite is INSERT OR REPLACE
			# rowid is a internal column in sqlite
			@stmt = @db.prepare('INSERT OR REPLACE INTO problems (rowid, id, title, body) VALUES (?, ?, ?, ?)')
			@db.run('BEGIN')

		@tpstart = Date.now()
		@done = 0

	fetchProblem: (id) =>
		@fetch @baseUrl + @problemPath + id, (body) =>
			@done++
			$ = cheerio.load(body)
			title = $('#content_body > center:nth-child(1) > span').text()
			body = $('#content_body').text()
			console.log "Now fetching ProblemID: #{id}, Title: #{title}"
			@stmt.run(id - @problemMin, id, title, body)
			@afterFetch() if @done == @problemCount

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

	fetchAllProblems: =>
		@prepareFetch()
		for i in [@problemMin..@problemMax]
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
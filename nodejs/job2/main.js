'use strict';
var sys = require('sys');
var http = require('http');
var jsdom = require('jsdom');
var sqlite3 = require('sqlite3');
var child_process = require('child_process');

function Spider() {
	//give an alias to this, to fill the js hell
	var parent = this;
	//prepare database
	//use sqlite's FTS(Full Text Search) table to store the data and perform quick search
	this.db = new sqlite3.Database('data.db');
	this.db.run('CREATE VIRTUAL TABLE IF NOT EXISTS problems USING fts4(id, title, body)');
	//define config
	this.baseUrl = 'http://acm.zju.edu.cn';
	this.indexPath = '/onlinejudge/showProblemsets.do';
	this.voluemPath = '/onlinejudge/showProblems.do?contestId=1&pageNumber=';
	this.problemPath = '/onlinejudge/showProblem.do?problemCode=';
	this.problemMin = 1001;

	//function define in prototype
	this.getVolumeCount = function() {
		jsdom.env({
			url: parent.baseUrl + parent.indexPath,
			done: function(errors, window) {
				parent.voluemCount = window.document.querySelectorAll('#content_body > form:nth-child(1) > a').length;
				//console.log(parent.voluemCount);
				parent.getProblemMax();
			}
		})
	}
	/* this function is deprecated
	 * because the problemID is continuous 
	 * and we don't have to access the problem from the voluem page
	 * just use problemPath and problemCode to access the problem
	 */
	this.getVoluemPathList = function() {
		jsdom.env({
			url: parent.baseUrl + parent.indexPath,
			done: function(errors, window) {
				parent.voluemPathList = window.document.querySelectorAll('#content_body > form:nth-child(1) > a')._toArray().map(function(item) {
					return item.getAttribute('href');
				})
				//console.log(parent.voluemPathList)
			}
		})
	}
	this.getProblemMax = function() {
		jsdom.env({
			url: parent.baseUrl + parent.voluemPath + parent.voluemCount,
			done: function(errors, window) {
				var $ = require('jquery')(window);
				parent.problemMax = $('#content_body > form:nth-child(1) > table > tr:last-child > td.problemId > a > font').text();
				parent.problemCount = parent.problemMax - parent.problemMin + 1;
				console.log(parent.problemMax + ' Problems in total');
				//start map
				parent.fetchAllProblems();
			}
		})
	}
	this.storeProblemContent = function(id) {
		// this request may take long time, so I use native http.client to handle it
		var url = parent.baseUrl + parent.problemPath + id;
		var req = http.get(url, function(res){
			var body = '';
			res.on('data', function(chunk){
				body += chunk;
			});
			res.on('end', function(){
				console.log('Fetched ProblemID: ' + id);
				parent.child.send([id, body]);
			});
		});
		req.on('error', function(e) {
			console.log('problem with request: ' + e.message);
		});
	};

	this.fetchAllProblems = function() {
		parent.db.serialize(function() {
			parent.stmt = parent.db.prepare('INSERT OR REPLACE INTO problems (rowid, id, title, body) VALUES (?, ?, ?, ?)');
			parent.db.run('BEGIN');
		});
		parent.tpstart = Date.now();
		parent.done = 0;

		// fork a separate process to parse the html
		parent.child = child_process.fork('./child.js');
		parent.child.on('message', function(m) {
			var id = m[0]
			var title = m[1];
			var body = m[2];
			parent.stmt.run(id - parent.problemMin, id, title, body);
			parent.done++;
			if (parent.done == parent.problemCount) {
				parent.tpend = Date.now();
				parent.child.disconnect();
				console.log('Fetch data used ' + (parent.tpend - parent.tpstart) / 1000 + ' s');

				console.log('Fetch data end, writing to database');
				parent.tpstart = Date.now();
				parent.db.serialize(function() {
					parent.db.run('COMMIT');
					parent.stmt.finalize();
				});
				parent.db.close(function() {
					parent.tpend = Date.now();
					console.log('Wirte to database used ' + (parent.tpend - parent.tpstart) / 1000 + ' s');
				});
			}
		});
		// map the burden
		for (var i = parent.problemMin; i <= parent.problemMax; i++) {
			parent.storeProblemContent(i);
		}
	}
}

try {
	var spider = new Spider();
	spider.getVolumeCount();
} catch(e) {
	console.log(e);
}
'use strict';
var http = require('http');
var jsdom = require('jsdom');
var sqlite3 = require('sqlite3');
var child_process = require('child_process');
var numCPUs = require('os').cpus().length;

function Spider(){
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
	
	//function define
	this.run = function(mode){
		parent.mode = mode;
		parent.getVolumeCount();
	}
	this.getVolumeCount = function(){
    	jsdom.env({
    		url: parent.baseUrl + parent.indexPath,
    		done: function (errors, window) {
    			parent.voluemCount = window.document.querySelectorAll('#content_body > form:nth-child(1) > a').length;
    			//console.log(parent.voluemCount);
    			window.close();
    			parent.getProblemMax();
    		}
		})
	}
	/* this function is deprecated
	 * because the problemID is continuous 
	 * and we don't have to access the problem from the voluem page
	 * just use problemPath and problemCode to access the problem
	 */
    this.getVoluemPathList = function(){
        jsdom.env({
            url: parent.baseUrl + parent.indexPath,
            done: function (errors, window) {
                parent.voluemPathList = window.document.querySelectorAll('#content_body > form:nth-child(1) > a')._toArray().map(function(item){
                    return item.getAttribute('href');
            	})
            	//console.log(parent.voluemPathList)
            	window.close();
        	}
    	})
	}
	this.getProblemMax = function(){
		jsdom.env({
    		url: parent.baseUrl + parent.voluemPath + parent.voluemCount,
    		done: function (errors, window) {
    			var $ = require('jquery')(window);
    			parent.problemMax = $('#content_body > form:nth-child(1) > table > tr:last-child > td.problemId > a > font').text();
    			parent.problemCount = parent.problemMax - parent.problemMin + 1;
    			console.log(parent.problemCount + ' Problems in total');
            	window.close();
    			if(parent.mode == 'parallel'){
    				parent.parallelFetchAllProblems();
    			} else{
    				parent.serializeFetchAllProblems();
    			}
    		}
		})
	}
	this.fetchStoreProblem = function(id){
		jsdom.env({
    		url: parent.baseUrl + parent.problemPath + id,	
    		done: function (errors, window) {
    			var $ = require('jquery')(window);
    			var title = $('#content_body > center:nth-child(1) > span').text();
    			var body = $('#content_body').text();
    			console.log('Now fetching ProblemID: ' + id + ', Title: ' + title);
				parent.stmt.run(id - parent.problemMin, id, title, body);
				parent.done++;
				window.close();
				if(parent.done == (parent.problemCount)){
					parent.afterFetch();
				}
    		}
		})
	}
	this.prepareFetch = function(){
		parent.db.serialize(function() {
			//UPSERT in sqlite is INSERT OR REPLACE
			//rowid is a internal column in sqlite
			parent.stmt = parent.db.prepare('INSERT OR REPLACE INTO problems (rowid, id, title, body) VALUES (?, ?, ?, ?)');
			parent.db.run('BEGIN');
		});
		parent.tpstart = Date.now();
		parent.done = 0;
	}
	this.afterFetch = function(){
		parent.tpend = Date.now();
		console.log('Fetch data used ' + (parent.tpend - parent.tpstart)/1000 + ' s');
					
		console.log('Fetch data end, writing to database');
		parent.tpstart = Date.now();
		parent.db.serialize(function() {
			parent.db.run('COMMIT');
			parent.stmt.finalize();
		});
		parent.db.close(function(){
			parent.tpend = Date.now();
			console.log('Wirte to database used ' + (parent.tpend - parent.tpstart)/1000 + ' s');
			parent.exit();
		});
	}
	this.serializeFetchAllProblems = function(){
		parent.prepareFetch();
		for(var i = parent.problemMin; i <= parent.problemMax; i++){
    		parent.fetchStoreProblem(i);
    	}
	}
	this.fetchProblem = function(id) {
		// this request may take long time, so I use native http.client to handle it
		var url = parent.baseUrl + parent.problemPath + id;
		var req = http.get(url, function(res){
			var body = '';
			res.on('data', function(chunk){
				body += chunk;
			});
			res.on('end', function(){
				console.log('Fetched ProblemID: ' + id);
				parent.child[id % numCPUs].send([id, body]);
			});
		});
		req.on('error', function(e) {
			console.log('problem with request: ' + e.message);
		});
	};
	this.storeProblem = function (id, title, body) {
		parent.stmt.run(id - parent.problemMin, id, title, body);
		parent.done++;
		if (parent.done == parent.problemCount) {
			parent.afterFetch();
		}
	}
	this.parallelFetchAllProblems = function() {
		parent.prepareFetch();
		// fork child process to parse the html
		parent.child = [];
		for (var i = 0; i < numCPUs; i++) {
			parent.child[i] = child_process.fork('./child.js');
			parent.child[i].on('message', function(m) {
				//id, title, body = m[0], m[1], m[2]
				parent.storeProblem(m[0], m[1], m[2]);
			});
		};
		// map the burden
		for (var i = parent.problemMin; i <= parent.problemMax; i++) {
			parent.fetchProblem(i);
		}
	}
	this.selectAllProblems = function(){
		parent.db.each('SELECT * FROM problems', function(err, row){
			console.log(row);
		})
	}
	this.queryProblems = function(keyword){
		parent.db.each('SELECT id, title FROM problems WHERE body MATCH ?', keyword, function(err, row){
			console.log('ProblemID: ' + row.id + ', Title: ' + row.title + ', Link: ' + parent.baseUrl + parent.problemPath + row.id);
		}, function(err, count){
			console.log(count + ' problems match your keyword');
			parent.exit();
		})
	}
	this.getItemCount = function(){
		parent.db.get('SELECT COUNT(*) AS count FROM problems', function(error, row){
			console.log('Database have ' + row.count + ' problems stored now');
		})
	};
	this.exit = function(){
		process.exit(0);
	}
}

exports.Spider = Spider;
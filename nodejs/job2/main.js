"use strict";
var jsdom = require('jsdom');
var sqlite3 = require('sqlite3');

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
	this.problemMin = 2001;
	
	//function define in prototype
	this.getVolumeCount = function(){
    	jsdom.env({
    		url: parent.baseUrl + parent.indexPath,
    		done: function (errors, window) {
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
    this.getVoluemPathList = function(){
        jsdom.env({
            url: parent.baseUrl + parent.indexPath,
            done: function (errors, window) {
                parent.voluemPathList = window.document.querySelectorAll('#content_body > form:nth-child(1) > a')._toArray().map(function(item){
                    return item.getAttribute('href');
            	})
            	//console.log(parent.voluemPathList)
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
    			console.log(parent.problemMax + ' Problems in total');
    			//start map
    			parent.fetchAllProblems();
    		}
		})
	}
	this.storeProblemContent = function(id){
		jsdom.env({
    		url: parent.baseUrl + parent.problemPath + id,	
    		done: function (errors, window) {
    			var $ = require('jquery')(window);
    			var title = $('#content_body > center:nth-child(1) > span').text();
    			var body = $('#content_body').text();
    			console.log('Now fetching ProblemID: ' + id + ', Title: ' + title);
				parent.stmt.run(id - parent.problemMin, id, title, body);
				parent.done++;
				if(parent.done == (parent.problemCount)){
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
					});
				}
    		}
		})
	}
	this.fetchAllProblems = function(){
		parent.db.serialize(function() {
			parent.stmt = parent.db.prepare('INSERT OR REPLACE INTO problems (rowid, id, title, body) VALUES (?, ?, ?, ?)');
			parent.db.run('BEGIN');
		});
		parent.tpstart = Date.now();
		parent.done = 0;
		//UPSERT in sqlite is INSERT OR REPLACE
		//rowid is a internal column in sqlite
		for(var i = parent.problemMin; i <= parent.problemMax; i++){
    		parent.storeProblemContent(i);
    	}
	}
}

try{
	var spider = new Spider();
	spider.getVolumeCount();
} catch(e){
	console.log(e);
}
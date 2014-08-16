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
	//UPSERT in sqlite is INSERT OR REPLACE
	//rowid is a internal column in sqlite
	this.stmt = this.db.prepare('INSERT OR REPLACE INTO problems (rowid, id, title, body) VALUES (?, ?, ?, ?)');
	//define config
	this.baseUrl = 'http://acm.zju.edu.cn';
	this.indexPath = '/onlinejudge/showProblemsets.do';
	this.voluemPath = '/onlinejudge/showProblems.do?contestId=1&pageNumber=';
	this.problemPath = '/onlinejudge/showProblem.do?problemCode=';
	
	//function define in prototype
	this.getVolumeCount = function(){
    	jsdom.env({
    		url: parent.baseUrl + parent.indexPath,
    		done: function (errors, window) {
    			parent.voluemCount = window.document.querySelectorAll('#content_body > form:nth-child(1) > a').length;
    			//console.log(parent.voluemCount);
    			parent.getProblemCount();
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
	this.getProblemCount = function(){
		jsdom.env({
    		url: parent.baseUrl + parent.voluemPath + parent.voluemCount,
    		done: function (errors, window) {
    			var $ = require('jquery')(window);
    			parent.problemCount = $('#content_body > form:nth-child(1) > table > tr:last-child > td.problemId > a > font').text();
    			console.log(parent.problemCount + ' Problems in total');
    			//start map
    			parent.fetchAllProblems();
    		}
		})
	}
	this.storeProblemContent = function(id){
		var parent = this;
		jsdom.env({
    		url: parent.baseUrl + parent.problemPath + id,	
    		done: function (errors, window) {
    			var $ = require('jquery')(window);
    			var title = $('#content_body > center:nth-child(1) > span').text();
    			var body = $('#content_body').text();
    			console.log('Now fetching ProblemID: ' + id + ', Title: ' + title);
    			// UPSERT in sqlite is INSERT OR REPLACE
				// rowid is a internal column in sqlite
				parent.stmt.run(id-1000, id, title, body);
				if(id == parent.problemCount){
					console.log("The End.");
					parent.stmt.finalize();
					parent.db.close();
				}
    		}
		})
	}
	this.fetchAllProblems = function(){
		for(var i = 1001; i <= parent.problemCount; i++){
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
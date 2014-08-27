// Generated by CoffeeScript 1.8.0
(function() {
  'use strict';
  var Spider, engine, fs, running, search;

  fs = require('fs');

  engine = require('./Spider');

  process.on('uncaughtException', function(err) {
    return console.log(err);
  });

  console.log('==Welcome to search engine for ZOJ==');

  if (fs.existsSync('data.db')) {
    console.log('Local database is update on ' + fs.statSync('data.db').mtime);
    Spider = new engine.Spider();
    Spider.getItemCount();
  } else {
    console.log("Local database hasn't build");
    Spider = new engine.Spider();
  }

  console.log('Usage:');

  console.log('[1] update the local database in single process');

  console.log('[2] update the local database in multi process');

  console.log('[3] search problems');

  running = false;

  search = false;

  process.stdin.setEncoding('utf8');

  process.stdin.on('data', function(chunk) {
    if (!running) {
      chunk = chunk.replace('\n', '');
      switch (chunk) {
        case '1':
          Spider.run();
          return running = true;
        case '2':
          Spider.run('parallel');
          return running = true;
        case '3':
          console.log('Please enter the keyword: ');
          return search = true;
        default:
          if (search) {
            Spider.queryProblems(chunk);
            return running = true;
          } else {
            console.log('>_< You typed something silly, byebye');
            return process.exit(0);
          }
      }
    }
  });

}).call(this);

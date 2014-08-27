// Generated by CoffeeScript 1.8.0
(function() {
  'use strict';
  var counter, http, req_done, req_generated, req_made, request, url;

  http = require('http');

  req_generated = req_made = req_done = 0;

  url = 'http://localhost:8080';

  request = function() {
    var req;
    req_generated++;
    req = http.get(url, function(res) {
      var body;
      req_made++;
      body = '';
      res.on('data', function(chunk) {
        return body += chunk;
      });
      return res.on('end', function() {
        return req_done++;
      });
    });
    req.on('error', function(e) {
      return console.log("problem with request: " + e.message);
    });
    return setImmediate(request);
  };

  counter = function() {
    console.log("Requests: " + req_generated + " generated; " + req_made + " made; " + req_done + " done");
    req_generated = req_made = req_done = 0;
    return setTimeout(counter, 1000);
  };

  setTimeout(counter, 1000);

  request();

}).call(this);
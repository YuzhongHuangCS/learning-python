var jsdom = require('jsdom');

process.on('uncaughtException', function(err) {
    console.log(err);
});

process.on('message', function(m) {
	var id = m[0]
	var html = m[1]
	jsdom.env(html, function(errors, window) {
		var $ = require('jquery')(window);
		var title = $('#content_body > center:nth-child(1) > span').text();
		var body = $('#content_body').text();
		console.log('Parsed ProblemID: ' + id + ', Title: ' + title);
		process.send([id, title, body]);
		window.close();
	});
});
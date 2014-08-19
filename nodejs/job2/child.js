var jsdom = require('jsdom');

process.on('uncaughtException', function(err) {
    console.log(err, err.stack);
});

process.on('message', function(m) {
	var id = m[0]
	var body = m[1]
	jsdom.env(body, function(errors, window) {
		var $ = require('jquery')(window);
		var title = $('#content_body > center:nth-child(1) > span').text();
		var body = $('#content_body').text();
		console.log('Parsed ProblemID: ' + id + ', Title: ' + title);
		process.send([id, title, body]);
		window.close();
	});
});
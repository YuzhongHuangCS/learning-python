http = require 'http'

server = http.createServer (req, res) ->
	res.writeHeader 200, {"Content-Type": "text/html"}
	res.write "</p>HttpVersion: #{req.httpVersion} </p>";
	res.write JSON.stringify req.headers
	res.end()

server.listen 8080
console.log 'httpd start @8080'
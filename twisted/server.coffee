http = require 'http'

server = http.createServer (req, res) ->
	res.writeHeader 200, {"Content-Type": "text/html"}
	res.write '<p>Headers:</p>'
	res.write JSON.stringify req.headers
	res.write '<hr/><p><i>Powered by nodejs</i></p>'
	res.end()

server.listen 8080
console.log 'httpd start @8080'
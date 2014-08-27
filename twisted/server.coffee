http = require 'http'

server = http.createServer((req, res) ->
	res.writeHeader 200, {"Content-Type": "text/plain"}
	res.write 'From nodejs'
	res.end
)

server.listen 8080;
console.log 'httpd start @8080'
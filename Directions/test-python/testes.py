#!/usr/bin/python3

api_key = "5b3ce3597851110001cf6248209f07136a7a44c0be17479e56a02c78"

theURL = "https://api.openrouteservice.org/v2/directions/driving-car?api_key=5b3ce3597851110001cf6248209f07136a7a44c0be17479e56a02c78&start=8.681495,49.41461&end=8.687872,49.420318"

######################
### Odoo JSON:

import odoolib
connection = odoolib.get_connection(hostname="localhost", port=8013, protocol="jsonrpc", database="odoo13_dirscache", login="admin", password="baygon")
user_model = connection.get_model("directions.route.request")
user_model.get_route(8.681495000, 49.414610000, 8.687872000, 49.420318000)

######################

wget "http://localhost:8013/jsonrpc" --post-data '{"jsonrpc": "2.0", "method": "call", "params": {"service": "common", "method": "login", "args": ["odoo13_dirscache", "admin", "admin"] }, "id": 124658997 }' -O- --save-headers --header="Content-Type: application/json" -o /dev/null

######################
POST /jsonrpc HTTP/1.1
User-Agent: Wget/1.19.4 (linux-gnu)
Accept: */*
Accept-Encoding: identity
Host: localhost:8013
Connection: Keep-Alive
Content-Type: application/x-www-form-urlencoded
Content-Length: 155

{"jsonrpc": "2.0", "method": "call", "params": {"service": "common", "method": "login", "args": ["odoo13_dirscache", "admin", "admin"] }, "id": 124658997 }

HTTP/1.0 400 BAD REQUEST
Content-Type: text/html
Content-Length: 152
Server: Werkzeug/0.11.15 Python/3.6.8
Date: Wed, 03 Jun 2020 02:53:03 GMT

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<title>400 Bad Request</title>
<h1>Bad Request</h1>
<p>Session expired (invalid CSRF token)</p>
#######################
POST /jsonrpc HTTP/1.1
Host: localhost:8013
User-Agent: python-requests/2.20.0
Accept-Encoding: gzip, deflate
Accept: */*
Connection: keep-alive
Content-Type: application/json
Content-Length: 153

{"jsonrpc": "2.0", "method": "call", "params": {"service": "common", "method": "login", "args": ["odoo13_dirscache", "admin", "admin"] }, "id": 793200492}

HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 48
Server: Werkzeug/0.11.15 Python/3.6.8
Date: Wed, 03 Jun 2020 02:54:18 GMT

{"jsonrpc": "2.0", "id": 793200492, "result": 2}






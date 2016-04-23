import httplib
import json
connection = httplib.HTTPConnection("localhost", 8080, strict=True)
connection.request("GET", "/ping")
response = json.load(connection.getresponse())
print response['data']

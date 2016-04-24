import httplib
import json


class CamelClient(object):

  host = None
  port = 0
  token = None

  def __init__(self, host, port):
    self.host = host
    self.port = port

  def Connect(self):
    response = self.Request("POST", "/users")
    self.token = response['json']['token']

  def Disconnect(self):
    assert self.token is not None, "You are not connected"
    self.Request("DELETE", "/users/{0}".format(self.token))

  def Version(self):
    return self.Request("GET", "/service/version")

  def Status(self):
    return self.Request("GET", "/service/status")

  def Ping(self):
    return self.Request("GET", "/ping")

  def Hump(self, style, raw):
    return self.Request("GET",
        "/humps/{0}?style={1}".format(raw, style))

  def Request(self, method, route):
    connection = httplib.HTTPConnection(self.host, self.port, strict=True)
    connection.request(method, route)
    response = connection.getresponse()
    body = response.read()

    return {
        "status": response.status,
        "json": json.loads(body) if body else None }

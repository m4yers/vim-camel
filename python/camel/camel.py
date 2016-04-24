from paths import CamelPaths

import subprocess
import socket
import errno
import httplib
import json
import time


class CamelClient(object):

  _host = None
  _port = 0
  _paths = None
  _token = None
  _server_popen = None

  def __init__(self, root, host, port):
    self._paths = CamelPaths(root)
    self._host = host
    self._port = port

  def Connect(self, startService=True):
    assert self._token is None, "Already connected"

    response = self._Request("POST", "/users")
    error = response['error']

    if error == 0:
      self._token = response['json']['token']
      print 'Token ', self._token
      return 0

    # We want to try create new service only once
    if not startService:
      return 1

    # Seems server is not running
    if error == errno.ECONNREFUSED:
      if not self._ServiceStart():
        return 1

    return self.Connect(False)

  def Disconnect(self):
    if self._token:
      self._Request("DELETE", "/users/{0}".format(self._token))
      self._ServiceStop()
      self._token = None

  def Version(self):
    return self._Request("GET", "/service/version")

  def Status(self):
    if self._ServiceIsAlive():
      # TODO GET /service/status
      return { 'alive': True, 'pid': self._server_popen.pid }
    else:
      return { 'alive': False }

  def Ping(self):
    return self._Request("GET", "/ping")

  def Hump(self, style, raw):
    return self._Request("GET",
        "/humps/{0}?style={1}".format(raw, style))

  def _Request(self, method, route, timeout = 2):
    try:
      connection = httplib.HTTPConnection(
          self._host,
          self._port,
          strict=True,
          timeout=timeout)
      connection.request(method, route)
      response = connection.getresponse()
      body = response.read()
    except socket.error as e:
      print 'Socket Error ' + str(e)
      return { "error" : e.errno }
    except:
      print 'Exception'

    return {
        # TODO fix this, should be None but freaking vim cannot convert it
        "error": 0,
        "status": response.status,
        "json": json.loads(body) if body else None }


  #######################
  #  Service lifecycle  #
  #######################

  def _ServiceStart(self):
    assert not self._ServiceIsAlive(), "Server is already running"
    args = [
        self._paths.Python(),
        self._paths.Server(),
        'start',
        '--host={0}'.format(self._host),
        '--port={0}'.format(self._port),
        '--stdout={0}'.format(self._paths.ServerStdOut()),
        '--stderr={0}'.format(self._paths.ServerStdErr())
    ]

    self._server_popen = subprocess.Popen(
        args,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)

    print 'Service:'
    print str(args)

    # wait 200ms till server fully started
    time.sleep(0.2)

    return self._ServiceIsAlive()

  def _ServiceStop(self):
    if self._ServiceIsAlive():
      self._server_popen.terminate()
      self._server_popen = None

  def _ServiceIsAlive(self):
    # When the process hasn't finished yet, poll() returns None.
    return self._server_popen is not None and self._server_popen.poll() is None

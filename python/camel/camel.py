from paths import CamelPaths

import subprocess
from threading import Thread
import socket
import errno
import httplib
import json
import time


class CamelClient(object):

  _opts = None
  _paths = None
  _token = None
  _enabler = None

  def __init__(self, opts):
    self._paths = CamelPaths(opts.root)
    self._opts = opts

  def Enable(self):

    # We are currently trying to enable the service
    if self._enabler is not None:
      return

    self._enabler = CamelServiceEnableThread(self._opts, self._paths)
    self._enabler.start()

  def Disable(self):
    # TODO terminate enabling thread here
    if self._token:
      _Request(self._opts, "DELETE", "/users/{0}".format(self._token))
      self._token = None

  def Version(self):
    if not self._IsEnabled():
      print 'Service is not enabled'
      return

    return _Request(self._opts, "GET", "/service/version")

  def Ping(self):
    if not self._IsEnabled():
      print 'Service is not enabled'
      return

    return _Request(self._opts, "GET", "/ping")

  def Hump(self, style, raw):
    if not self._IsEnabled():
      print 'Service is not enabled'
      return

    return _Request(self._opts, "GET",
        "/humps/{0}?style={1}".format(raw, style))

  def _IsEnabled(self):
    if self._enabler is None:
      return self._token is not None

    if self._enabler.is_alive():
      return False

    self._token = self._enabler.get_token()
    self._enabler = None

    return self._token is not None


class CamelServiceEnableThread(Thread):

  def __init__(self, opts, paths):
    Thread.__init__(self)
    self._opts = opts
    self._paths = paths
    self._token = None

  def run(self):
    error = self._Connect()
    if error == 0:
      return

    # Seems server is not running
    if error == errno.ECONNREFUSED:
      if self._ServiceStart():
        while self._Connect() != 0:
          time.sleep(1)
        print "after"

  def _Connect(self):
    response = _Request(self._opts, "POST", "/users", timeout = 10)
    error = response['error']

    if error == 0:
      self._token = response['json']['data']['token']
      print 'Token ', self._token
      return 0

    return error

  def _ServiceStart(self):
    args = [
        self._paths.Python(),
        self._paths.Server(),
        'start',
        '--host={0}'.format(self._opts.host),
        '--port={0}'.format(self._opts.port),
        '--dict={0}'.format(self._paths.Dictionary() +
          ',{0}'.format(','.join(self._opts.dicts))),
        '--stdout={0}'.format(self._paths.ServerStdOut()),
        '--stderr={0}'.format(self._paths.ServerStdErr())
    ]

    self._server_popen = subprocess.Popen(
        args,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)

    print 'Service:'
    print str(args)

    return True

  def get_token(self):
    return self._token


def _Request(opts, method, route, timeout = 2):

  try:
    connection = httplib.HTTPConnection(
        opts.host,
        opts.port,
        strict=True,
        timeout=timeout)
    connection.request(method, route)
    response = connection.getresponse()
    body = response.read()
  except socket.error as e:
    return { "error" : e.errno }

  return {
      "error": 0,
      "status": response.status,
      "json": json.loads(body) if body else None }


class CamelOptions(object):
  host = None
  port = 0
  root = None
  dicts = list()

  def SetAddress(self, host, port):
    self.host = host
    self.port = port

  def SetRoot(self, root):
    self.root = root

  def AddDicts(self, dicts):
    self.dicts.extend(dicts)

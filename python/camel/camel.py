from paths import CamelPaths

import subprocess
from threading import Thread
import socket
import errno
import httplib
import json
import time


class CamelClient(object):

  def __init__(self, opts):
    self._paths = CamelPaths(opts.root)
    self._opts = opts
    self._enabler = None

    with open('{}/VERSION'.format(self._paths.Root())) as v:
      self._version = v.readline().rstrip()

  def Enable(self):

    # We are currently trying to enable the service
    if self._enabler is not None:
      return

    self._enabler = CamelServiceEnableThread(self._opts, self._paths)
    self._enabler.start()

  def Disable(self):
    pass

  def Version(self):
    if not self._IsEnabled():
      print 'Camel is not enabled'
      return

    return _Request(self._opts, "GET", "/service/version")['json']['data']

  def Ping(self):
    if not self._IsEnabled():
      print 'Camel is not enabled'
      return

    return _Request(self._opts, "GET", "/ping")['json']['data']

  def Status(self):
    if not self._IsEnabled():
      print 'Camel is not enabled'
      return

    result = _Request(self._opts, "GET", "/status")['json']['data']
    result['client.root'] = self._paths.Root()
    result['client.version'] = self._version
    return result

  def Hump(self, style, raw):
    if not self._IsEnabled():
      print 'Camel is not enabled'
      return

    return _Request(self._opts, "GET",
        "/humps/{0}?style={1}".format(raw, style)).json.data

  def _IsEnabled(self):
    if self._enabler is None:
      return True

    if self._enabler.is_alive():
      return False

    self._enabler = None

    return True


class CamelServiceEnableThread(Thread):

  def __init__(self, opts, paths):
    Thread.__init__(self)
    self._opts = opts
    self._paths = paths

  def run(self):
    error = self._Ping()

    if error == 0:
      return

    # Seems server is not running
    if error == errno.ECONNREFUSED:
      if self._ServiceStart():
        while self._Ping() != 0:
          time.sleep(1)

  def _Ping(self):
    response = _Request(self._opts, "GET", "/ping", timeout = 10)
    error = response['error']

    if error == 0:
      return 0

    return error

  def _ServiceStart(self):
    args = [
        self._paths.Python(),
        self._paths.Server(),
        'start',
        '--root={}'.format(self._paths.Root()),
        '--host={}'.format(self._opts.host),
        '--port={}'.format(self._opts.port),
        '--dict={}'.format(self._paths.Dictionary() +
          ',{}'.format(','.join(self._opts.dicts))),
        '--stdout={}'.format(self._paths.ServerStdOut()),
        '--stderr={}'.format(self._paths.ServerStdErr())
    ]

    self._server_popen = subprocess.Popen(
        args,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)

    return True


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

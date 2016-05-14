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
    self._starter = None
    self._restarter = None

    with open('{}/VERSION'.format(self._paths.Root())) as v:
      self._version = v.readline().rstrip()

  def Enable(self):

    # We are currently trying to enable the service
    if self._starter is not None:
      return

    self._starter = Thread(target=self._Enable)
    self._starter.start()

  def _Enable(self):
    error = self._Ping()

    if error == 0:
      return

    # Seems server is not running
    if error == errno.ECONNREFUSED:
      if self._ServiceStart():
        while self._Ping() != 0:
          time.sleep(1)

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

  def Disable(self):
    pass

  def RestartService(self):
    self._restarter = Thread(target=self._RestartService)
    self._restarter.start()

  def _RestartService(self):
    # If we were enabling the service we need to wait till the job is done
    if self._starter is not None:
      self._starter.join()

    # Kill the service
    self._Request("DELETE", "/service")

    # Wait till the service is dead
    while self._Ping() == 0:
      time.sleep(1)

    # Start the service again
    self._starter = Thread(target=self._Enable)
    self._starter.start()
    self._starter.join()

  def Version(self):
    return self._Request("GET", "/service/version")['json']['data']

  def Ping(self):
    return self._Request("GET", "/ping")['json']['data']

  def Status(self):
    result = self._Request("GET", "/status")

    if result['error'] == 0:
      result = result['json']['data']
    else:
      result = dict()
      if self._restarter is not None:
        result['server.restarting'] = True
      else:
        result['server.starting'] = True

    result['client.root'] = self._paths.Root()
    result['client.version'] = self._version
    return result

  def Hump(self, style, raw):
    result = self._Request("GET", "/humps/{0}?style={1}".format(raw, style))
    return result['json']['data']

  def IsEnabled(self):
    if self._starter is not None and self._starter.is_alive():
      return False
    else:
      self._starter = None

    if self._restarter is not None and self._restarter.is_alive():
      return False
    else:
      self._restarter = None

    return self._starter is None and self._restarter is None

  def _Ping(self):
    response = self._Request("GET", "/ping", timeout = 10)
    error = response['error']

    if error == 0:
      return 0

    return error

  def _Request(self, method, route, timeout = 2):

    try:
      connection = httplib.HTTPConnection(
          self._opts.host,
          self._opts.port,
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

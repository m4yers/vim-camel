from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn

import threading
import argparse
import urlparse
import json
import re

from tst import TST


_service = None


class CamelRequestHandler(BaseHTTPRequestHandler):

  data = dict()
  status = 200

  def do_POST(self):
    global _service

    route = urlparse.urlparse(self.path)

    if route.path == '/users':
      print 'post users'
      self.send_response(200)
      self.send_header('Content-Type', 'application/json')
      self.end_headers()
      self.wfile.write("{\"token\":\"blah-blah-blah\"}")

  def do_GET(self):
    global _service

    route = urlparse.urlparse(self.path)

    if route.path == '/ping':
      print 'ping'
      self.send_response(200)
      self.send_header('Content-Type', 'application/json')
      self.end_headers()
      self.wfile.write("{\"data\":\"Pong\"}")
    elif re.search('/humps/[^/]*', route.path):
      word = route.path.split('/')[-1].lower()
      self.Status(200)
      self.Data(_service.ToCamelCase(word))
      self.Finish()

  def do_DELETE(self):
    global _service

    route = urlparse.urlparse(self.path)
    # query = urlparse.parse_qs(route.query)

    # This shutdowns the service
    if route.path == '/service':
      _service.stop()
      self.send_response(204)
      self.end_headers()
    elif re.search('/users/[^/]*', route.path):
      print 'delete users'
      self.send_response(204)
      self.end_headers()

  def Status(self, status):
    self.status = status

  def Data(self, data):
    self.data = data

  def Finish(self):
    self.send_response(self.status)
    self.send_header('Content-Type', 'application/json')
    self.end_headers()
    json.dump({"data": self.data}, self.wfile)
    # self.wfile.write(json.dumps({"data": data}))


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
  pass


class CamelService():

  def __init__(self, host, port):
    self.server = ThreadedHTTPServer((host, port), CamelRequestHandler)
    self.tst = TST()

    # test data
    words = [ "use", "user", "no", "not", "found",
        "except", "exception", "io", "ion"]
    for word in words:
      self.tst.Put(word, word)

  def start(self):
    self.server_thread = threading.Thread(target=self.server.serve_forever)
    # self.server_thread.daemon = True
    self.server_thread.start()

  def waitForThread(self):
    self.server_thread.join()

  def stop(self):
    self.server.shutdown()
    self.waitForThread()

  def ToCamelCase(self, string):
    result = list()
    groups = list()
    self._BreakIntoWords(string, groups, list(), "")
    for group in groups:
      current = ""
      for word in group:
        current += word.title()

      result.append(current)

    return result

  def _BreakIntoWords(self, string, groups, current, bad):
    assert len(string) != 0, "Must not be empty"
    # Use longest matches first
    prefixes = self.tst.AllPrefixesOf(string)[::-1]

    if len(prefixes) == 0:
      bad += string[0:1]
      string = string[1:]
      if len(string) == 0:
        current.append(bad)
        groups.append(current)
      else:
        self._BreakIntoWords(string, groups, current, bad)
    else:
      for prefix in prefixes:
        # Add non matched part of string as unknown word
        if len(bad) != 0:
          current.append(bad)
          bad = ""

        clone = current[:]
        clone.append(prefix)

        rest = string[len(prefix):]
        if len(rest) == 0:
          groups.append(clone)
        else:
          self._BreakIntoWords(rest, groups, clone, bad)


def ParseArguments():
  parser = argparse.ArgumentParser(prog='Camel',
      description='Makes word casing easier')

  subparsers = parser.add_subparsers(title='Actions', dest='action')

  parser_start = subparsers.add_parser('start', help='Start Camel daemon')

  parser_start.add_argument('--host', type=str,
      default='127.0.0.1',
      help='service hostname')

  # Default of 0 will make the OS pick a free port for us
  parser_start.add_argument('--port', type=int,
      default=0,
      help='service port')

  parser_start.add_argument('--log', metavar='LEVEL', type=str,
      default='info',
      choices=['debug', 'info', 'warning', 'error', 'critical'],
      help='log level')

  return parser.parse_args()


if __name__ == "__main__":
  args = ParseArguments()
  print 'Camel HTTP Server {}:{}'.format(args.host, args.port)
  _service = CamelService(args.host, args.port)
  _service.start()

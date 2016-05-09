from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn

import threading
import argparse
import urlparse
import random
import json
import time
import re
import sys

from tst import TST


SERVICE_KILL_TIME = 60.0 * 60 * 3 # 3hrs
_service = None


class CamelRequestHandler(BaseHTTPRequestHandler):

  data = dict()
  status = 200

  def handle(self):
    _service.Touch()
    BaseHTTPRequestHandler.handle(self)

  def do_GET(self):
    global _service

    route = urlparse.urlparse(self.path)

    if route.path == '/ping':
      self.Status(200)
      self.Data("Pong")
      self.Finish()
    elif re.search('/humps/[^/]*', route.path):
      word = route.path.split('/')[-1].lower()
      self.Status(200)
      self.Data(_service.ToCamelCase(word))
      self.Finish()

  def do_DELETE(self):
    global _service

    route = urlparse.urlparse(self.path)

    # This shutdowns the service
    if route.path == '/service':
      self.Status(204)
      self.Finish()
      _service.Stop()

  def Status(self, status):
    self.status = status

  def Data(self, data):
    self.data = data

  def Finish(self):
    self.send_response(self.status)
    if self.data is not None:
      self.send_header('Content-Type', 'application/json')
    self.end_headers()
    json.dump({"data": self.data}, self.wfile)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
  pass


class CamelService():

  def __init__(self, host, port, dicts):
    self._server = ThreadedHTTPServer((host, port), CamelRequestHandler)
    self._tst = TST()
    self._last_time = time.time()
    self._last_time_lock = threading.Lock()
    self._kill_timer = None

    for fdict in dicts:
      self._AddDictionary(fdict)

  def Touch(self):
    with self._last_time_lock:
      self._last_time = time.time()

  def TimerUpdate(self, delay = SERVICE_KILL_TIME):
    if self._kill_timer is not None:
      self._kill_timer.cancel()

    self._kill_timer = threading.Timer(delay, self._CheckStatus)
    self._kill_timer.start()

  def TimerKill(self):
    if self._kill_timer:
      self._kill_timer.cancel()
      self._kill_timer = None

  def _CheckStatus(self):
    with self._last_time_lock:
      now = time.time()
      diff = now - self._last_time

      if diff < SERVICE_KILL_TIME:
        self.TimerUpdate(SERVICE_KILL_TIME - (diff))
        return

      print 'No activity for the last {} seconds'.format(SERVICE_KILL_TIME)
      self.Stop()

  def Start(self):
    self._server_thread = threading.Thread(target=self._server.serve_forever)
    # self._server_thread.daemon = True
    self._server_thread.start()
    self.TimerUpdate()

  def Stop(self):
    self.TimerKill()
    self._server.shutdown()
    self._server_thread.join()

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

  def _AddDictionary(self, fdict):
    words = [word.rstrip('\n') for word in open(fdict)]

    print 'Got {} words'.format(len(words))

    # This prevents worst case time for TST since horizontaly it is a list
    random.shuffle(words)

    for word in words:
      if len(word) > 1:
        self._tst.Put(word, word)

  def _BreakIntoWords(self, string, groups, current, bad):
    assert len(string) != 0, "Must not be empty"
    # Use longest matches first
    prefixes = self._tst.AllPrefixesOf(string)[::-1]

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
  parser = argparse.ArgumentParser(prog='Camel', description='Hump your input')

  subparsers = parser.add_subparsers(title='Actions', dest='action')

  parser_start = subparsers.add_parser('start', help='Start Camel service')

  parser_start.add_argument('--host', type=str, default='127.0.0.1')

  # TODO Default of 0 will make the OS pick a free port for us
  parser_start.add_argument('--port', type=int, default=0)

  parser_start.add_argument('--dict', type=str, required=True)

  parser_start.add_argument('--stdout', type=str)
  parser_start.add_argument('--stderr', type=str)

  parser_start.add_argument('--log', metavar='LEVEL', type=str,
      default='info',
      choices=['debug', 'info', 'warning', 'error', 'critical'],
      help='log level')

  return parser.parse_args()


if __name__ == "__main__":
  args = ParseArguments()

  if args.stdout is not None:
    print 'change stdout'
    sys.stdout = open( args.stdout, 'w' )

  if args.stderr is not None:
    print 'change stderr'
    if args.stdout == args.stderr:
      sys.stderr = sys.stdout
    else:
      sys.stderr = open( args.stderr, 'w' )

  print 'Camel HTTP Server {}:{}'.format(args.host, args.port)

  _service = CamelService(args.host, args.port, args.dict.split(','))
  _service.Start()

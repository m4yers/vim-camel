from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn

import concurrent.futures
import threading
import argparse
import urlparse
import random
import json
import time
import re
import sys
import os

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
    elif route.path == '/status':
      self.Status(200)
      self.Data(_service.Status())
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

  def __init__(self, host, port):
    self._host = host
    self._port = port
    self._tst = TST()
    self._start_time = time.time()
    self._last_time = self._start_time
    self._last_time_lock = threading.Lock()
    self._kill_timer = None

  def Status(self):
    status = dict()
    status['version'] = 0.1 # read from file on startup
    status['stdout'] = sys.stdout.name
    status['stderr'] = sys.stderr.name
    status['address'] = '{}:{}'.format(self._host, self._port)
    status['pid'] = os.getpid()
    status['words'] = self._tst.Size()
    return status

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
    print 'CamelService Start'
    self._server = ThreadedHTTPServer(
      (self._host, self._port), CamelRequestHandler)
    self._server_thread = threading.Thread(target=self._server.serve_forever)
    # self._server_thread.daemon = True
    self._server_thread.start()
    self.TimerUpdate()

  def Stop(self):
    print 'CamelService Stop'
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

  def AddDictionaries(self, dicts):
    tsts = dict()

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
      for fdict in dicts:
        futures = list()
        words = list()
        letter = ""
        for word in [word.rstrip('\n') for word in open(fdict)]:
          # this assumes the dictionary is in lower-case order
          if word[0].lower() == letter.lower():
            words.append(word)
          else:
            tst = tsts.get(letter, TST())
            tsts[letter] = tst
            futures.append(executor.submit(self.FillTST, tst, words))
            letter = word[0].lower()
            words = list(word)

        for future in concurrent.futures.as_completed(futures):
          try:
            tst = future.result()
          except Exception as e:
            print e

    for tst in tsts.values():
      # TODO Add posibility to merge two tsts if they are overlapping
      self._tst.Take(tst)

    print 'Added {} words'.format(self._tst.Size())

  def FillTST(self, tst, words):
    # This prevents worst case time for TST
    random.shuffle(words)

    for word in words:
      if len(word) > 1:
        tst.Put(word, word)
    return tst

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

  _service = CamelService(args.host, args.port)
  _service.AddDictionaries(args.dict.split(','))
  _service.Start()

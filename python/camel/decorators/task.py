from threading import Thread


class task(object):
  '''Task decorator'''

  def __init__(self, func):
    self._func = func
    self._obj = None
    self._thread = None
    self._result = None

  def __get__(self, obj, objtype):
    self._obj = obj
    return self

  def __call__(self, *args, **kwargs):
    return self.start(*args, **kwargs)

  def _run(self, *args, **kwargs):
    self._result = self._func(*args, **kwargs)

  def start(self, *args, **kwargs):
    args = ((self._obj,) + args)
    self._thread = Thread(target=self._run, args=args, kwargs=kwargs)
    self._thread.start()
    return self

  def wait(self):
    self._thread.join()

  def is_alive(self):
    return self._thread.is_alive()

  def result(self):
    return self._result

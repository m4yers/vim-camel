from threading import Lock


def synchronized(lock=None):
  '''Synchronization decorator.'''

  if not lock:
    lock = Lock()

  def wrap(f):
    def new_function(*args, **kw):
      lock.acquire()
      try:
        return f(*args, **kw)
      finally:
        lock.release()
    return new_function
  return wrap

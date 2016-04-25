import tempfile
import stat
import os

ACCESSIBLE_TO_ALL_MASK = ( stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH |
                           stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP )


class CamelPaths(object):

  def __init__(self, _root):
    self._root = _root
    self._temp = self.Temp()

  def Python(self):
    return "python"

  def Root(self):
    return self._root

  def Dictionary(self):
    return os.path.join(self._root, 'dict', 'foldoc.txt')

  def Server(self):
    return os.path.join(self._root, 'python', 'camel', 'cameld.py')

  def ServerStdOut(self):
    return os.path.join(self._temp, 'cameld.out')

  def ServerStdErr(self):
    return os.path.join(self._temp, 'cameld.err')

  def Temp(self):
    path = os.path.join( tempfile.gettempdir(), 'camel_tmp' )
    try:
      os.makedirs(path)
      current_stat = os.stat(path)
      flags = current_stat.st_mode | ACCESSIBLE_TO_ALL_MASK
      os.chmod(path, flags)
    except OSError:
      # Folder already exists, skip folder creation.
      pass

    return path

import tempfile
import stat
import os

ACCESSIBLE_TO_ALL_MASK = ( stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH |
                           stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP )


class CamelPaths(object):

  def __init__(self, root):
    self.root = root
    self.temp = self.Temp()

  def Python(self):
    return "python"

  def Server(self):
    return self.root + "/python/camel/cameld.py"

  def ServerStdOut(self):
    return os.path.join(self.temp, 'cameld.out')

  def ServerStdErr(self):
    return os.path.join(self.temp, 'cameld.err')

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

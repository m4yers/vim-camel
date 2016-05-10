class TST(object):

  def __init__(self):
    self._root = None
    self._size = 0

  def __str__(self):
    return '[TST size {}]'.format(self._size)

  def Size(self):
    return self._size

  def _UpdateSize(self, x):
    ts = 1 if x.value is not None else 0
    ls = x.left.size if x.left is not None else 0
    rs = x.right.size if x.right is not None else 0
    ms = x.middle.size if x.middle is not None else 0
    x.size = ts + ls + rs + ms

  def Put(self, key, value):
    if value is None:
      self.Delete(key)
      return

    self._root = self._Put(self._root, key, value, 0)
    self._size = self._root.size

  def _Put(self, x, key, value, depth):
    char = key[depth]

    if not x:
      x = _Node(char)

    if char < x.char:
      x.left = self._Put(x.left, key, value, depth)
    elif char > x.char:
      x.right = self._Put(x.right, key, value, depth)
    elif depth < len(key) - 1:
      x.middle = self._Put(x.middle, key, value, depth + 1)
    else:
      x.value = value

    self._UpdateSize(x)
    return x

  def Delete(self, key):
    """Delete key from TST

    :key: Key to delete

    """
    self._Delete(self._root, key, 0)
    self._size = self._root.size

  def _Delete(self, x, key, depth):
    char = key[depth]

    if not x:
      x = _Node(char)

    if char < x.char:
      x.left = self._Put(x.left, key, depth)
    elif char > x.char:
      x.right = self._Put(x.right, key, depth)
    elif depth < len(key) - 1:
      x.middle = self._Put(x.middle, key, depth + 1)
    else:
      x.value = None

    # If there are no other nodes bellow we remove whole branch
    self._UpdateSize(x)
    return None if x.size == 0 else x

  def Get(self, key):
    node = self._Get(self._root, key, 0)
    if not node:
      return None

    return node.value

  def _Get(self, x, key, depth):
    if not x:
      return None

    char = key[depth]

    if char < x.char:
      return self._Get(x.left, key, depth)
    elif char > x.char:
      return self._Get(x.right, key, depth)
    elif depth < len(key) - 1:
      return self._Get(x.middle, key, depth + 1)

    return x

  def Take(self, other):
    """Take in other TST as sub trees

    :other: Other TST instance, MUST not contain overlapping nodes

    """

    if other.Size() == 0:
      return

    for tst in other.ToForest():
      assert tst._root.left is None
      assert tst._root.right is None
      self._root = self._Take(self._root, tst._root)

    self._size = self._root.size

  def _Take(self, x, other):
    if not x:
      return other

    if other.char == x.char:
      raise ValueError(
        'Passed TST contains overlapping {} nodes'.format(other.char))
    elif other.char < x.char:
      x.left = self._Take(x.left, other)
    elif other.char > x.char:
      x.right = self._Take(x.right, other)

    self._UpdateSize(x)
    return x

  def ToForest(self):
    """Split TST instance into a TST forest with a single root node.

    :tst: TST instance
    :returns: List of TST instances

    """

    result = list()
    self._ToForest(self._root, result)
    self._root = None
    self._size = 0
    return result

  def _ToForest(self, x, result):
    if not x:
      return

    self._ToForest(x.left, result)

    x.size = x.middle.size
    tst = TST()
    tst._root = x
    tst._size = x.size
    result.append(tst)

    self._ToForest(x.right, result)

    x.left = None
    x.right = None

  def All(self):
    """Return all keys it the TST instance

    :returns: List of all keys

    """

    result = list()
    self._All(self._root, "", result)
    return result

  def _All(self, x, prefix, result):
    if not x:
      return

    self._All(x.left, prefix, result)

    if x.value:
      result.append(prefix + x.char)

    self._All(x.middle, prefix + x.char, result)

    self._All(x.right, prefix, result)

  def AllPrefixesOfSize(self, size):
    """Returs all available string prefixes of argument size

    :size: Size
    :returns: All prefixes of argument size

    """

    result = list()
    self._AllPrefixesOfSize(self._root, size, "", result)
    return result

  def _AllPrefixesOfSize(self, x, size, prefix, result):
    """Collects all prefixes of argument size into result

    :x: TODO
    :size: TODO

    """

    if not x:
      return

    self._AllPrefixesOfSize(x.left, size, prefix, result)

    if size == 1:
      result.append(prefix + x.char)
    else:
      self._AllPrefixesOfSize(x.middle, size - 1, prefix + x.char, result)

    self._AllPrefixesOfSize(x.right, size, prefix, result)

  def AllPrefixesOf(self, string):
    collection = list()
    self._AllPrefixesOf(self._root, string, "", collection)
    return collection

  def _AllPrefixesOf(self, x, string, prefix, collection):
    if not x:
      return

    depth = len(prefix)

    if depth == len(string):
      return

    char = string[depth]

    if char < x.char:
      self._AllPrefixesOf(x.left, string, prefix, collection)
    elif char > x.char:
      self._AllPrefixesOf(x.right, string, prefix, collection)
    else:
      if x.value:
        collection.append(x.value)
      self._AllPrefixesOf(x.middle, string, prefix + char, collection)


class _Node(object):

  def __init__(self, char):
    self.char   = char
    self.left   = None
    self.middle = None
    self.right  = None
    self.value  = None
    self.size   = 0    # including itself if value is not None


# TODO move this into a separate test file,
# and write proper tests, for fuck sake
if __name__ == "__main__":
  words = [ "she", "sells", "sea", "shells", "by", "the", "sea", "shore"]
  tst = TST()

  for word in words:
    tst.Put(word, word)

  print tst.Size()

  for word in words:
    assert tst.Get(word) == word

  assert tst.Size() == len(set(words))

  # test Take
  others = ["wut", "green", "ecce"]
  otst = TST()
  for word in others:
    otst.Put(word, word)

  print otst.Size()

  tst.Take(otst)

  for word in words:
    assert tst.Get(word) == word

  for word in others:
    assert tst.Get(word) == word

  # test AllPrefixesOfSize
  prefixes = tst.AllPrefixesOfSize(2)
  assert len(prefixes) == 7

  print tst.Size()
  print tst.All()
  print [str(t) for t in tst.ToForest()]

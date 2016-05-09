class TST(object):

  _root = None

  def Put(self, key, value):
    self._root = self._Put(self._root, key, value, 0)

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

    return x

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

    self._Take(self._root, other._root)

    current = other._root
    while current is not None:
      current = current.left
      if current:
        self._root = self._Take(self._root, current)

    current = other._root
    while current is not None:
      current = current.right
      if current:
        self._root = self._Take(self._root, current)

  def _Take(self, x, other):
    if not x:
      return other

    if other.char == x.char:
      raise ValueError('Passed TST contains overlapping nodes')
    elif other.char < x.char:
      x.left = self._Take(x.left, other)
    elif other.char > x.char:
      x.right = self._Take(x.right, other)

    return x

  def AllPrefixesOf(self, string):
    collection = list()
    self._All(self._root, string, "", collection)
    return collection

  def _All(self, x, string, prefix, collection):
    if not x:
      return

    depth = len(prefix)

    if depth == len(string):
      return

    char = string[depth]

    if char < x.char:
      self._All(x.left, string, prefix, collection)
    elif char > x.char:
      self._All(x.right, string, prefix, collection)
    else:
      if x.value:
        collection.append(x.value)
      self._All(x.middle, string, prefix + char, collection)


class _Node(object):

  char   = None
  left   = None
  middle = None
  right  = None
  value  = None

  def __init__(self, char):
    self.char = char


if __name__ == "__main__":
  words = [ "she", "sells", "sea", "shells", "by", "the", "sea", "shore"]
  tst = TST()

  for word in words:
    tst.Put(word, word)

  for word in words:
    assert tst.Get(word) == word

  print tst.AllPrefixesOf("shells")

  # test Take
  others = ["green", "wut", "oops"]
  otst = TST()
  for word in others:
    otst.Put(word, word)

  tst.Take(otst)

  for word in words:
    assert tst.Get(word) == word

  for word in others:
    assert tst.Get(word) == word

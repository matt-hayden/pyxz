import collections

def moving(iterable, n=None, init=None):
    """
    Very simple generator that implements a lookback, returning a deque (of
    length n) for each element of input. Use the deque by indexing backwards:
    d[0] == latest element
    d[1] == previous element
    d[2] == two elements back

    Modifying this deque is supported:
    >>> for d in moving(range(6), n=4):
    ...     if d[0] == 2:
    ...             latest = d.popleft() # delete the latest element
    ...             print "Element '{}' skipped here".format(latest)
    ...             continue # or don't. See if I care
    ...     elif d[0] == 4: # modify elements in-place
    ...             d[-1] = 'I saw 4!'
    ...     print d
    deque([0], maxlen=4)
    deque([1, 0], maxlen=4)
    Element '2' skipped here
    deque([3, 1, 0], maxlen=4)
    deque([4, 3, 1, 'I saw 4!'], maxlen=4)
    deque([5, 4, 3, 1], maxlen=4)
    """
    if n: d = collections.deque([init]*n,n)
    else: d = collections.deque([],n)
    for this in iterable:
        d.appendleft(this)
        yield d
def is_range(iterable, if_empty=False):
    """
    True if the argument is equivalent to an integer interval. Behaviour for
    empty sets is the argument if_empty.
    """
    try:
        intset = set(int(_) for _ in iterable)
    except:
        return False
    n = len(intset)
    if n == 0: return if_empty
    elif n == 1: return True
    else:
        my_min, my_max = min(intset), max(intset)
#            if my_min == my_max: return True # unreachable?
        for i in xrange(my_min+1, my_max): # loops from [1] to [-2]
            if i not in intset: return False
        return True
def make_xrange(iterable):
    """
    Compresses an iterable of numbers into the equivalent xrange object.
    """
    c = Counter(int(i) for i in iterable)
    if not set(c.values()) - set(0) == set([1]):
        raise ValueError("iterable does not have unique integer keys")
    start, stop = min(c), max(c)
    if not len(c) == stop-start:
        raise ValueError("iterable is missing {} values".format(stop-start-len(c)))
    return xrange(start, stop+1) # should be functionally equivalent to c.elements()

# Neat trick to make simple trees:
# https://gist.github.com/hrldcpr/2012250
def tree():
    """
    Returns a dict of dicts, where assignment and node creation are
    automagically supported:
    >>> t=tree()
    >>> len(t['branch'])
    0
    >>> t['branch']='leaf'
    >>> len(t['branch'])
    4
    >>> t['branches']['b1']
    ...
    >>> t['branches']['b2']
    ...
    >>> len(t['branches'])
    2

    """
    return defaultdict(tree)
def tree_to_dicts(t):
    return {k: tree_to_dicts(t[k]) for k in t}
def tree_add_path(t, keys):
    for key in keys: t = t[key]

# Neat trick to make simple namespaces:
# http://stackoverflow.com/questions/4984647/accessing-dict-keys-like-an-attribute-in-python
class Namespace(dict):
    """
    An abstract class. Inheriting from this limits your class' functionality,
    but allows i['j'] and i.j to be assigned and used interchangably.
    >>> n=Namespace()
    >>> n.blues = 'brothers'
    >>> n['blues'] == 'brothers'
    True
    >>> n
    {'blues': 'brothers'}

    Pickling should work as expected:
    >>> import cPickle as pickle
    >>> s = pickle.dumps(n)
    >>> s2 = pickle.loads(s)
    >>> s2
    {'blues': 'brothers'}
    """
#       __slots__ = [ '__dict__' ] # sabotages pickle :)
    def __init__(self, *args, **kwargs):
        super(Namespace, self).__init__(*args, **kwargs)
        self.__dict__ = self
class Collapsible(object):
    # subclasses should define to_tuple()
    def __repr__(self):
        return self.__class__.__name__+str(self.to_tuple())
    def __reduce__(self):
        # return a text representation or a tuple like (Foo, args)
        return (self.__class__, self.to_tuple())
class CollapsibleNamespace(Namespace, Collapsible):
    def to_tuple(self, format=None):
        if format is None:
            try:
                format = self.format
            except:
                format = self._tuple._fields
        elif isinstance(format, basestring): format = format.split()
#               else: # format's doin just fine
        return self._tuple(*[self[_] for _ in format])
if __name__ == '__main__':
    import doctest
    results = doctest.testmod()

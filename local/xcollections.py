#! /usr/bin/env python
import collections
import math

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
    return collections.defaultdict(tree)
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
#
class SCounter(collections.Counter):
    """Drop-in replacement for Counter with statistics functions.
    """
    def dist(self, *args, **kwargs):
        '''GENERATOR
        '''
        cfreq = 0.
        NR = sum(self.values())
        #for key, freq in self.most_common(*args, **kwargs):
        for key, freq in sorted(self.iteritems()):
            freq = float(freq)
            cfreq += freq
            yield key, freq/NR, cfreq/NR
    @property
    def mean_stdev(self, population=True, quick=False):
        n = len(self)
        denom = n if population else (n-1)
        assert n
        s = math.fsum(x*f for (x, f) in self.iteritems())
        m = s/n if s else 0.
        #
        if quick:
            return m, None
        ss = math.fsum((x-m)**2*f for (x, f) in self.iteritems())
        v = (ss - m**2/n)/denom if ss else 0.
        return m, math.sqrt(v) if (v > 0) else 0
#
#
#
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


#! /usr/bin/env python
import collections
import math

from local.xmath import weighted_median

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
    _sum = math.fsum # the function for real numbers
    @property
    def n(self):
        return sum(self.values()) if self else 0
    @property
    def sum(self):
        return self._sum(x*f for (x,f) in self.iteritems()) if self else 0
    def get_psum(self, condition, **kwargs):
        return self._sum(x*f for (x,f) in self.iteritems() if condition(x, **kwargs)) if self else 0
    @property
    def mean(self):
        return self.sum/self.n
    def get_pmean(self, *args, **kwargs):
        return self.psum(*args, **kwargs)/self.n
    def get_median(self, **kwargs):
        return weighted_median(self.items(), **kwargs)
    def get_dist(self):
        '''GENERATOR
        '''
        cfreq = 0
        n = float(self.n)
        for key, freq in self.iteritems():
            cfreq += freq
            yield key, freq/n, cfreq/n
    def get_percentiles(self, *args, **kwargs):
        return weighted_percentiles(self.items(), *args, **kwargs)
    @property
    def mean(self):
        n = len(self)
        return self.sum/n if n else None
    def get_stdev(self, population=False):
        m, denom = self.mean, self.n if population else (self.n-1)
        ss = self._sum((x-m)*(x-m)*f for (x, f) in self.iteritems())
        v = ss/denom
        return math.sqrt(v) if (v > 0) else 0
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

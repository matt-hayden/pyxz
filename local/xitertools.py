#! /usr/bin/env python
import collections

def flatten(args):
	"""Simply filter an iterable of iterables into logically sequential atomic
	elements. """
	for el in args:
		if isinstance(el, basestring): yield el
		elif isinstance(el, collections.Iterable):
			for _ in flatten(el): yield _
		else: yield el
def groupby_diff(iterable, key):
	if not hasattr(iterable, '__next__'):
		iterable = iter(iterable)
	prev = next(iterable)
	stored = [prev]
	for this in iterable:
		if stored and key(prev, this):
			yield stored
			stored = [this]
		else:
			stored.append(this)
		prev = this
	if stored: yield stored
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
#!env python
import collections

def flatten(args):
	"""Simply filter an iterable of iterables into logically sequential atomic
	elements. """
	for el in args:
		if isinstance(el, basestring): yield el
		elif isinstance(el, collections.Iterable):
			for _ in flatten(el): yield _
		else: yield el
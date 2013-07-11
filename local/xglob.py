#!env python
import glob as _glob

from local.flatten import flatten

def glob(*args, **kwargs):
	fargs = list(flatten(args))
	if len(fargs) <= 1:
		return _glob.glob(*fargs)
	else:
#		return reduce(set.union, (set(glob(arg)) for arg in args))
		globs = [set(_glob.glob(_)) for _ in fargs]
		return set.union(*globs)
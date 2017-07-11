#!env python
import glob as _glob
import os.path

from local.flatten import flatten

def glob(*args, **kwargs):
	indir = kwargs.pop('indir', None)
	if indir:
		fargs = [os.path.join(indir, a) for a in flatten(args)]
	else:
		fargs = list(flatten(args))
	if len(fargs) <= 1:
		return _glob.glob(*fargs)
	else:
#		return reduce(set.union, (set(glob(arg)) for arg in args))
		globs = [set(_glob.glob(a)) for a in fargs]
		return set.union(*globs)
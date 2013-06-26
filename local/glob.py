from . import *
_glob=import_module('glob', '_glob')
def glob(*args, **kwargs):
	if len(args) <= 1:
		return _glob.glob(*args)
	else:
#		return reduce(set.union, (set(glob(arg)) for arg in args))
		return set.union(*(set(_glob.glob(arg)) for arg in args))
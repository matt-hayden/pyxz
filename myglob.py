from glob import glob
def myglob(*args, **kwargs):
	if len(args) <= 1:
		return glob(*args)
	else:
#		return reduce(set.union, (set(glob(arg)) for arg in args))
		return set.union(*(set(glob(arg)) for arg in args))
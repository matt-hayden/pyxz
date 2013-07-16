#!env python
"""
Cache (pickable) data that becomes stale after a predetermined amount of time.
"""
__version__ = '0'

from datetime import datetime, timedelta
import os.path
import cPickle as pickle

cache_stale_after = {'minutes': 15}

def cached(function,
		   args=(),
		   cache_file=None,
		   lifetime=timedelta(**cache_stale_after),
		   mode='pickle'):
	"""
	Define a function that returns a cacheable value that goes stale after a
	predetermined delay. For example, to use a value of now() that is at most
	15 minutes off:
	
	>>> @cached
	... def hello(*args):
	...     return datetime.now()
	...
	>>> print hello
	2013-07-16 13:57:35.335000
	
	~/.cache/function or ~/.function.cache will be printed if less than 15
	minutes old, or else function(*args) will be run, the output saved to one 
	of those 2 files, and also returned. To force regeneration, simply delete 
	the cache.
	Note that some argument in the above function definition is mandatory.
	Change the global variable cache_stale_after for alternative values:
	
	Examples:
		cache_stale_after = {'minutes': 1, 'seconds': 30}
		cache_stale_after = {'days': 30.5}
	"""
	def age(filename):
		mode, inode, dev, nlink, uid, gid, size, atime, mtime, ctime = os.stat(filename)
		return datetime.now() - datetime.fromtimestamp(mtime)
	name = function.__name__
	if not cache_file:
		cache_dir = os.path.expanduser('~/.cache')
		if os.path.isdir(cache_dir):
			cache_file = os.path.join(cache_dir, name)
		else:
			cache_file = os.path.expanduser('~/.{}.cache'.format(name))
	#
	if os.path.exists(cache_file) and (age(cache_file) < lifetime):
		if mode == 'pickle':
			return pickle.load(open(cache_file))
		else:
			return open(cache_file).read()
	else:
		content = function(*args)
		with open(cache_file, 'wb') as fo:
			if mode == 'pickle':
				pickle.dump(content, fo)
			else:
				fo.write(str(content))
		return content

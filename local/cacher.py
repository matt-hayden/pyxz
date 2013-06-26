from datetime import datetime, timedelta
import os.path
from cPickle import dump, load
from cStringIO import StringIO

def cached(function,
		   args = (),
		   cache_file = None,
		   lifetime = timedelta(minutes=15)):
	"""
	Use like this:
	
	@cached
	def hello(*args):
		return datetime.now()
	print hello
	
	~/.cache/hello or ~/.hello.cache will be printed if less than 15 minutes
	old, or else hello(*args) will be run, the output saved to one of those 2
	files, and also printed. To force regeneration, simply delete the cache.
	Note that some argument in the above function definition is mandatory.
	"""
	def age(filename):
		mode, inode, dev, nlink, uid, gid, size, atime, mtime, ctime = os.stat(filename)
		return datetime.now() - datetime.fromtimestamp(mtime)
	name = function.__name__
	if not cache_file:
		if os.path.isdir(os.path.expanduser('~/.cache')):
			cache_file = '~/.cache/{}'.format(name)
		else:
			cache_file = '~/.{}.cache'.format(name)
	cache_file = os.path.expanduser(cache_file)
	#
	if os.path.exists(cache_file) and (age(cache_file) < lifetime):
#		return open(cache_file).read()
		return load(open(cache_file))
	else:
#		return tee(function(*args), cache_file)
		content = function(*args)
		with open(cache_file, 'wb') as fo:
			dump(content, fo)
		return content
#
from datetime import datetime
import os
import stat

class mode(list): # TODO
	def __init__(self, data):
		if isinstance(data, basestring):
			self.from_string(data)
		elif isinstance(data, int):
			self.from_int(data)
		else:
			super(mode, self).__init__(data)
	def __int__(self):
		sum(m*8**p for p,m in enumerate(reversed(self)))
	def __str__(self):
		return ''.join(str(m) for m in self)
	def from_int(self, mode_int):
		self.from_string(oct(mode_int))
	def from_string(self, mode_text):
		self = mode([ int(c) for c in mode_text ])

def stat(*args, **kwargs):
	"""
	Wrapper around os.stat() that returns slightly more human numbers
	"""
	stat = os.stat(*args)
	if kwargs.pop('mode_tuple', False):
		mymode = [ int(c) for c in oct(stat.st_mode) ]
	else:
		mymode = stat.st_mode
	atime = datetime.fromtimestamp(stat.st_atime)
	mtime = datetime.fromtimestamp(stat.st_mtime)
	ctime = datetime.fromtimestamp(stat.st_ctime)
	return os.stat_result((mymode, stat.st_ino, stat.st_dev, stat.st_nlink,
						   stat.st_uid, stat.st_gid, stat.st_size, atime, mtime,
						   ctime))
#def isdir(*args):
#	st = stat(*args)
#	return st if st.st_mode[-5] & 4 else False
#def isfile(*args):
#	st = stat(*args)
#	return st if st.st_mode[-5] & 1 else False

def get_stat_type(mode, like_ls=False):
	"""
	Return a one-character code for the type of a filesystem object. Can be
	used with a os.stat() object or an integer mask.
	"""
	if isinstance(mode, collections.Iterable):
		mode = sum(m*8**p for p,m in enumerate(reversed(t)))
	elif not isinstance(mode, int):
		mode = mode.st_mode
	if stat.S_ISDIR(mode):		return 'd'
	elif stat.S_ISCHR(mode):	return 'c'
	elif stat.S_ISBLK(mode):	return 'b'
	elif stat.S_ISREG(mode):	return '-'
	elif stat.S_ISFIFO(mode):	return 'p'
	elif stat.S_ISLNK(mode):	return 'l'
	elif stat.S_ISSOCK(mode):	return 's'
	else:						return '?' if like_ls else 'U'
#!env python
"""Working with platform-independent stat objects.
"""
from datetime import datetime
import os
import stat

from xcollections import Namespace

stat_fields = 'st_mode st_ino st_dev st_nlink st_uid st_gid st_size st_atime st_mtime st_ctime'.split()

class xstat(Namespace):
	@staticmethod
	def from_stat(statresult):
		s = xstat(zip(stat_fields, statresult))
		s.is_dir	=	stat.S_ISDIR(s.st_mode)
		s.is_file	=	stat.S_ISREG(s.st_mode)
		s.is_link	=	stat.S_ISLNK(s.st_mode)
		return s
	@property
	def atime(self): return datetime.fromtimestamp(self.st_atime)
	@property
	def ctime(self): return datetime.fromtimestamp(self.st_ctime)
	@property
	def mtime(self): return datetime.fromtimestamp(self.st_mtime)
	

class xst_mode(list):
	def __init__(self, data):
		if isinstance(data, basestring):
			self.from_string(data)
		elif isinstance(data, int):
			self.from_int(data)
		else:
			super(xst_mode, self).__init__(data)
	def __int__(self):
		sum(m*8**p for p,m in enumerate(reversed(self)))
	def __str__(self):
		return ''.join(str(m) for m in self)
	def from_int(self, mode_int):
		self.from_string(oct(mode_int))
	def from_string(self, mode_text):
		super(xst_mode, self).__init__(int(c, base=8) for c in mode_text)
#
### WRONG:
'''
def stat(*args, **kwargs):
	"""Wrapper around os.stat() that returns python datetimes and indexable 
	modes.
	
	Arguments:
		mode=True will return an object of decoded mode. For example, mode
		511 base 10, 0777 base 8, will be returned as [0,7,7,7].
	"""
	strict = kwargs.pop('strict', True)
	stat = os.stat(*args)
	if strict:
		mymode = xst_mode(stat.st_mode)
	else:
		mymode = stat.st_mode
	atime = datetime.fromtimestamp(stat.st_atime)
	mtime = datetime.fromtimestamp(stat.st_mtime)
	ctime = datetime.fromtimestamp(stat.st_ctime)
	if strict:
		return os.stat_result((mymode, stat.st_ino, stat.st_dev, stat.st_nlink,
							   stat.st_uid, stat.st_gid, stat.st_size, atime, mtime,
							   ctime))
	else:
		return Namespace(st_mode=mymode,
						 st_ino=stat.st_ino or None,
						 st_dev=stat.st_dev or None,
						 st_nlink=stat.st_nlink,
						 st_uid=stat.st_uid,
						 st_gid=stat.st_gid,
						 st_size=stat.st_size,
						 st_atime=atime,
						 st_mtime=mtime,
						 st_ctime=ctime)
'''
def convert_mode(format, mode):
	if format=='ls':
		text = bytearray('-'*10)
		if m & 1: text[9] = 'x'
		m >>= 1
		if m & 1: text[8] = 'w'
		m >>= 1
		if m & 1: text[7] = 'r'
		m >>= 1
		if m & 1: text[6] = 'x'
		m >>= 1
		if m & 1: text[5] = 'w'
		m >>= 1
		if m & 1: text[4] = 'r'
		m >>= 1
		if m & 1: text[3] = 'x'
		m >>= 1
		if m & 1: text[2] = 'w'
		m >>= 1
		if m & 1: text[1] = 'r'
		m >>= 1
		if m: text[0] = get_stat_type(mode)
		return text
#def isdir(*args):
#	st = stat(*args)
#	return st if st.st_mode[-5] & 4 else False
#def isfile(*args):
#	st = stat(*args)
#	return st if st.st_mode[-5] & 1 else False

def get_stat_type(mode):
	"""
	Return a one-character code for the type of a filesystem object. Can be
	used with a os.stat() object or an integer mask.
	"""
	if isinstance(mode, xst_mode):
		mode = int(mode)
	elif not isinstance(mode, int):
		mode = mode.st_mode
	if stat.S_ISDIR(mode):		return 'd'
	elif stat.S_ISCHR(mode):	return 'c'
	elif stat.S_ISBLK(mode):	return 'b'
	elif stat.S_ISREG(mode):	return '-'
	elif stat.S_ISFIFO(mode):	return 'p'
	elif stat.S_ISLNK(mode):	return 'l'
	elif stat.S_ISSOCK(mode):	return 's'
	else:						return '?'
def get_ls_type(mode):
	c = get_stat_type(mode)
	return 'U' if c == '?' else c


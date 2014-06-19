#!env python
"""Working with platform-independent stat objects.
"""
from datetime import datetime
import os
import stat

from xcollections import Namespace

stat_fields = 'st_mode st_ino st_dev st_nlink st_uid st_gid st_size st_atime st_mtime st_ctime'.split()

class XStat(Namespace):
	@staticmethod
	def from_stat(statresult):
		s = XStat(zip(stat_fields, statresult))
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
def xstat(*args, **kwargs):
	return XStat.from_stat(os.stat(*args, **kwargs))

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


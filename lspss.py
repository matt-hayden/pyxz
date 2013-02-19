
from glob import glob
import os.path
import sys

import spssaux

from console_size import get_terminal_size

def fmtcols(mylist, cols = None, sep=None):
	"""Inspired by:
	http://stackoverflow.com/questions/171662/formatting-a-list-of-text-into-columns#173823
	"""
	sl = max(len(str(x)) for x in mylist)
	if cols is None:
		lines, columns = get_terminal_size()
		cols = columns//sl
		if cols < 1:
			cols = 1
	if sep is None:
		lines = (''.join(x.ljust(sl) for x in mylist[i:i+cols]) for i in xrange(0,len(mylist),cols))
	else:
		lines = (sep.join(mylist[i:i+cols]) for i in xrange(0,len(mylist),cols))
	return '\n'.join(lines)

args = sys.argv[1:] or glob('*.sav')
for arg in args:
	dirname, basename = os.path.split(arg)
	filepart, ext = os.path.splitext(basename)
	spssaux.OpenDataFile(filespec=arg, filetype=ext[1:4])
	varnames=spssaux.getVariableNamesList()
	varnames.sort(key=lambda x:x.upper())
	print fmtcols(varnames)
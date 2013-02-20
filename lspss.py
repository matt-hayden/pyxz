
from glob import glob
from itertools import izip_longest
import os.path
import sys

import spssaux

from console_size import get_terminal_size

def fmtcols(mylist, cols = None, sep=None):
	"""Inspired by:
	http://stackoverflow.com/questions/171662/formatting-a-list-of-text-into-columns#173823
	"""
	sl = max(len(str(x)) for x in mylist)
	n = len(mylist)
	if cols is None:
		term_rows, term_columns = get_terminal_size()
		cols = term_columns//sl
	if cols < 1:
		cols = 1
	rows = (n//cols)+1
	partitioned = [mylist[i:i+rows] for i in xrange(1,len(mylist),rows)]
	if sep is None:
#		lines = (''.join(x.ljust(sl) for x in mylist[i:i+cols]) for i in xrange(0,len(mylist),cols))
		width_by_partition = [ (max(len(x) for x in el), el) for el in partitioned ]
		justified = [ [x.ljust(j) for x in el] for j, el in width_by_partition ]
		lines = (' '.join(x) for x in zip(*justified))
	else:
#		lines = (sep.join(mylist[i:i+cols]) for i in xrange(0,len(mylist),cols))
		lines = (sep.join(x) for x in zip(*partitioned))
	return '\n'.join(lines)

args = sys.argv[1:] or glob('*.sav')
for arg in args:
	dirname, basename = os.path.split(arg)
	filepart, ext = os.path.splitext(basename)
	spssaux.OpenDataFile(filespec=arg, filetype=ext[1:4])
	varnames=spssaux.getVariableNamesList()
	if False:
		varnames.sort(key=lambda x:x.upper())
	if sys.stdout.isatty():
		print fmtcols(varnames)
	else:
		print '\n'.join(varnames)
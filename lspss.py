#! env python
import argparse
from glob import glob
#from itertools import izip_longest
import os.path
import sys

import spssaux

from local.console.size import to_columns

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='List SPSS variables in a file')
	group = parser.add_mutually_exclusive_group() # 'sort_order', help='Sort by:')
	group.add_argument('-I', help="variable order in file")
	group.add_argument('-n', help="variable name, case insensitive")
	group.add_argument('-N', help="variable name, case sensitive")
	parser.add_argument('input_files', nargs='*')
	args = parser.parse_args()
	print args.input_files
	if not args.input_files:
		args.input_files = glob('*.sav')
	if not args.input_files:
		dirname, basename = os.path.split(sys.argv[0])
		filepart, ext = os.path.splitext(basename)
		print filepart, "({})".format(sys.argv[0]), "usage:"
		print basename, "[files...]"
	for path in args.input_files:
		dirname, basename = os.path.split(path)
		filepart, ext = os.path.splitext(basename)
		spssaux.OpenDataFile(filespec=path, filetype=ext[1:4])
		varnames=spssaux.getVariableNamesList()
		if False:
			varnames.sort(key=lambda x:x.upper())
		if sys.stdout.isatty():
			print to_columns(varnames)
		else:
			print '\n'.join(varnames)
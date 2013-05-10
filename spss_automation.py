from collections import defaultdict
from itertools import groupby
import os
import os.path

import spssaux

def form_one_line(label, ticks, nticks=None, start=1, missing_symbol='_', tick_symbol=None, label_width=50):
	"""
	Input: label, ticks
		label is a string, usually the name of a variable
		ticks is an iterable of integers, probably a set
	Output: a string like '| label | 1 _ 3 4 _' for (label, [1,3,4])
	"""
	label = label[-1*label_width:].ljust(label_width)
	try:
		nticks = nticks or max(ticks)
		test_indexes = range(start, nticks+start)
	except:
		nticks = 0
		test_indexes = []
	if not tick_symbol:
		tickbar = ' '.join(str(n) if n in ticks else missing_symbol for n in test_indexes)
	else:
		tickbar = ' '.join(tick_symbol if n in ticks else missing_symbol for n in test_indexes)
	return '| '+label+' | '+tickbar
#
def spss_get_common_variables(input_filenames, 
							  name_key=lambda _: _.lower(), 
							  sort_key=lambda _: len(_[-1]), 
							  sort_reverse=True,
#							  prefix=""
							  ):
	"""
	Input: a list of SAV files
	Output: a combined list of variables that appear in one or more of those files
	"""
	assert hasattr(name_key, '__call__')
	input_filenames = [ os.path.abspath(_) for _ in input_filenames ]
#	prefix = prefix or os.path.commonprefix(input_filenames+[os.path.abspath(os.curdir)])
	#
	var_names_by_fileorder = defaultdict(set)
	for i, f in enumerate(input_filenames, start=1):
#		print " ", i, "=", f.replace(prefix,"",1) if prefix else f
		print " ", i, "=", os.path.relpath(f)
		spssaux.OpenDataFile(f)
		for v in spssaux.VariableDict():
			if name_key:
				var_names_by_fileorder[name_key(v.VariableName)].add(i)
			else:
				var_names_by_fileorder[v.VariableName].add(i)
	###
	s = var_names_by_fileorder.items() # pairs of variable name, [index of file(s) present]
	
	s.sort()
	s.sort(key=sort_key, reverse=sort_reverse) # descending coverage, by default
	return s
#
def spss_print_common_variables(input_filenames, 
								grouper=None,
								group_seperator=None):
	"""
	Input: a list of SAV files
	Output: a text table of variables sorted by frequency of occurance
	"""
	number_of_input_files = len(input_filenames)
	if not grouper:
		def grouper(name_fis_tuple):
			# name_fis_tuple is an element from s above
			name, fis = name_fis_tuple
			nfis = len(fis)
			if nfis == number_of_input_files:
				return 1
			elif nfis == 1:
				return 4
			elif nfis > number_of_input_files/2:
				return 2
			else:
				return 3
	# assume spss_get_common_variables(input_filenames) is sorted by frequency of occurrance
	s=spss_get_common_variables(input_filenames)
	label_width = max(len(_[0]) for _ in s)
	if group_seperator is None:
		group_seperator = '-'*(label_width+4)
	for coverage_group, name_fis_tuples in groupby(s, grouper):
		if group_seperator:
			print group_seperator
		for name, fis in name_fis_tuples:
			print form_one_line(name, fis, nticks=number_of_input_files, label_width=label_width)
			
if __name__ == '__main__':
	from glob import glob
	import sys
	#
	args = sys.argv[1:] or glob('*.SAV')
	if args:
		if all(os.path.exists(_) for _ in args):
			spss_print_common_variables(args)
		else:
			for f in args:
				print f, "Found" if os.path.exists(f) else "Not Found!"
	else:
		print "No .SAV files given"
		sys.exit(-1)
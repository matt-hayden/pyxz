#! env python

from spss_file import *

from console_size import condense_string # this function is probably misplaced
#
def variable_description_string(vdtuple, widths = [0]*6, line_width = None):
	"""
	Formats (order, label, name, level, missing, flags) into a sensible
	fixed-width string. The display widths can be controlled by widths[], 
	which is ordered like above.	
	"""
	order, label, name, level, missing, flags = vdtuple
	text = ' '.join((str(order).rjust(widths[0] or 4)+flags.ljust(widths[5] or 3),
					 name.ljust(widths[2] or 20),
					 level.ljust(widths[3] or 10),
					 str(missing),
					 label
					 ))
	if line_width:
		too_long = len(text) - line_width
		if too_long > 0:
			label_width = len(label)
			new_label = condense_string(label, label_width-too_long)
			return variable_description_string((order, new_label, name, level, missing, flags), widths, line_width)
	return text
def label_and_tick_string(label, ticks, nticks=None, start=1, missing_symbol='_', tick_symbol=None, label_width=50):
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
	return label+' | '+tickbar
#
def spss_print_variables(filename,
						 key=None,
						 reverse=False,
						 line_width=None):
	"""
	Input: one file
	"""
	vars = spss_load_variables(filename)
	widths = {}
	widths[0] = len(str(vars[-1][0]))
	for i in range(1,6):
		widths[i] = max(len(_[i]) for _ in vars)
	vars.sort()
	if key:
		vars.sort(key=key, reverse=reverse)
	for v in vars:
		print variable_description_string(v, widths=widths, line_width=line_width)
#
def spss_print_common_variables(args,
								key=None,
								reverse=False):
	"""
	Input: multiple files
	Output: text of variables occuring in at least one of the input files
	"""
	input_filenames = list(args)
	number_of_input_files = len(input_filenames)
	s=spss_get_common_variables(input_filenames)
	label_width = max(len(_[0]) for _ in s)
	s.sort()
	if key:
		s.sort(key=key, reverse=reverse)
	for name, fis in s:
		print label_and_tick_string(name, fis, nticks=number_of_input_files, label_width=label_width)
#
def spss_print_common_variables_by_file(args,
										key=None,
										reverse=False):
	"""
	Input: multiple files
	Output: text that looks like terminals in The Matrix
	"""
	input_filenames = list(args)
	number_of_input_files = len(input_filenames)
	if not key:
		def key(name_fis_tuple, indices=range(1,number_of_input_files+1)):
			name, fis = name_fis_tuple
			return [ _ in fis for _ in indices ]
		reverse=True
	return spss_print_common_variables(input_filenames, key=key, reverse=reverse)
#
def spss_print_common_variable_coverage(args,
										key=None,
										reverse=False):
	"""
	Input: multiple files
	Output: text like spss_print_common_variables_by_file, but sorted by frequency
	"""
	input_filenames = list(args)
	number_of_input_files = len(input_filenames)
	if not key:
		def key(name_fis_tuple, indices=range(1,number_of_input_files+1)):
			name, fis = name_fis_tuple
			return (len(fis), [ _ in fis for _ in indices ])
		reverse=True
	return spss_print_common_variables(input_filenames, key=key, reverse=reverse)
#
def spss_print_colliding_variables(*args, **kwargs):
	"""
	A wrapper for spss_get_colliding_variables() for the command-line.
	"""
	slist = kwargs.pop('varname_descriptions', None)
	if not slist:
		slist = sorted(spss_get_colliding_variables(*args, **kwargs))
	if not slist:
		return
	namewidth = max(len(name) for name, collisions in slist)
	filenamewidth = max(len(filename) for varname, _ in slist for filename, collisions in _ )
	indent = ''.rjust(namewidth)
	print
	print "{} variables found to have incompatible types or missing values".format(len(slist))
	for varname, collisions in slist:
		rhs = varname.rjust(namewidth)
		for filename, (myname, mytype, mymissing) in sorted(collisions):
			print rhs, "\t".join((filename.ljust(filenamewidth), mytype, str(mymissing)))
			rhs = indent
		print
#
if __name__ == '__main__':
	from glob import glob
	import sys
	#
	from console_size import get_terminal_size
	#
	args = sys.argv[1:] or glob('*.SAV')
	if sys.stdout.isatty():
		rows, columns = get_terminal_size()
	else:
		rows, columns = None, None
	#
	if args:
		if len(args) == 1:
			spss_print_variables(args.pop(), line_width=columns-1 if columns else None)
		else:
			if all(os.path.exists(_) for _ in args):
				spss_print_common_variable_coverage(args)
#				spss_print_common_variables(args)
			else:
				for f in args:
					print f, "Found" if os.path.exists(f) else "Not Found!"
	else:
		print "No .SAV files given"
		sys.exit(-1)
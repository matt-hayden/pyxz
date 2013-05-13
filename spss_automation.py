from collections import defaultdict, namedtuple
from itertools import groupby
from logging import debug, info, warning, error, critical
import os.path
import cPickle as pickle

import spssaux

from console_size import condense_string, redirect_terminal
#
vdtuple_field_order = {'ORDER':0, 'LABEL':1, 'NAME':2, 'LEVEL':3, 'MISSING':4, 'FLAGS':5}
def vdtuple_field_order_keyer(arg):
	if hasattr(arg, '__call__'):
		return arg
	if isinstance(arg, str):
		value = arg.upper()
		if value not in vdtuple_field_order:
			warning("Sort value not recognized: {}".format(value))
			return None
		elif value in ['ID', 'ORDER']:
			value = None
		elif value in ['LABEL', 'NAME', 'LEVEL', 'MISSING', 'FLAGS']:
			return vdtuple_field_order_keyer[vdtuple_field_order[value]]
	if isinstance(arg, int):
		return lambda _:_[arg].upper()
### both name and factory need to have the same name for pickle
SPSS_Variable_Description = namedtuple('SPSS_Variable_Description',
									   [n for n,o in sorted(vdtuple_field_order.items(),key=lambda _:_[-1])] )
#
def vdtuple(spss_variable,
			flags = None,
			missing_values_none = (0, None, None, None),
			factory = SPSS_Variable_Description):
	"""
	Returns (order, label, name, level, missing, flags)
	"""
	my_flags = flags.upper() if flags else ''
	#
	my_level = spss_variable.VariableLevel
	if my_level == 'nominal' and spss_variable.VariableType > 0:
#		my_level = 'string ({:3d})'.format(spss_variable.VariableType)
		my_level = 'string ({})'.format(spss_variable.VariableType)
	#
	if 'units' in spss_variable.Attributes and 'U' not in my_flags:
		my_flags += 'U'
	if 'U' in my_flags:
		my_units = spss_variable.Attributes.pop('units','unit').strip()
		my_level += ' ({})'.format(my_units)
	#
	my_missing = spss_variable.MissingValues2
	if my_missing == missing_values_none:
		my_missing = ''
	elif 'M' not in my_flags:
		my_flags += 'M'
	#
	return factory(spss_variable.VariableIndex,
				   spss_variable.VariableLabel,
				   spss_variable.VariableName,
				   my_level,
				   my_missing,
				   my_flags)
def variable_description_string(vdtuple, widths = [0]*6, line_width = None):
	"""
	Formats (order, label, name, level, missing, flags) into a sensible fixed-width
	string.
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
	return '| '+label+' | '+tickbar
#
def spss_get_common_variables(input_filenames, 
							  name_key=lambda _: _.lower(), 
							  sort_key=lambda _: len(_[-1]), 
							  sort_reverse=True,
							  cached=True
							  ):
	"""
	Input: a list of SAV files
	Output: a combined list of variables that appear in one or more of those files
	"""
	if name_key:
		assert hasattr(name_key, '__call__')
#	input_filenames = [ os.path.abspath(_) for _ in input_filenames ]
	#
	var_names_by_fileorder = defaultdict(set)
	###
	if cached:
		for i, f in enumerate(input_filenames, start=1):
			print " ", i, "=", os.path.relpath(f)
			vars = spss_load_variables(f)
			for order, label, name, level, missing, flags in vars:
				if name_key:
					var_names_by_fileorder[name_key(name)].add(i)
				else:
					var_names_by_fileorder[name].add(i)
	else:
		for i, f in enumerate(input_filenames, start=1):
			print " ", i, "=", os.path.relpath(f)
			spssaux.OpenDataFile(os.path.normpath(f))
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
def spss_load_variables(filename, pickle_filename = '', save=True):
	"""
	SPSS v20 seems to print a lot to stdout. This function discards that output.
	"""
	pickle_filename = pickle_filename or filename+'.variables'
	vars = []
	#
	if os.path.exists(pickle_filename) and (os.path.getmtime(filename) <= os.path.getmtime(pickle_filename)):
		try:
			with open(pickle_filename, 'rb') as fi:
				vars = pickle.load(fi)
		except Exception as e:
			info("Loading {} failed: {}".format(pickle_filename, e))
	if not vars:
		spssaux.OpenDataFile(os.path.normpath(filename))
		with redirect_terminal(stdout=os.devnull):
			filter_var = spssaux.GetDatasetInfo('Filter')
			info("Filter variable '{}'".format(filter_var))
			weight_var = spssaux.GetDatasetInfo('Weight')
			info("Weight variable '{}'".format(weight_var))
			split_var = spssaux.GetDatasetInfo('SplitFile')
			info("Split variable '{}'".format(split_var))
			for v in spssaux.VariableDict():
				flags = ''
				n = v.VariableName
				if n == filter_var:
					flags += 'F'
				if n == weight_var:
					flags += 'W'
				if n == split_var:
					flags += 'S'
				vars.append(vdtuple(v, flags=flags))
		if save:
			try:
				with open(pickle_filename, 'wb') as fo:
					pickle.dump(vars, fo)
			except IOError as e:
				info("Saving {} failed: {}".format(pickle_filename, e))
	return vars
#
def spss_print_variables(filename, key=None, reverse=False, line_width=None):
	"""
	"""
	vars = spss_load_variables(filename)
	widths = {}
	widths[0] = len(str(vars[-1][0]))
	for i in range(1,6):
		widths[i] = max(len(_[i]) for _ in vars)
	if key:
		vars.sort(key=vdtuple_field_order_keyer(key), reverse=reverse)
	for v in vars:
		print variable_description_string(v, widths=widths, line_width=line_width)
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
			print label_and_tick_string(name, fis, nticks=number_of_input_files, label_width=label_width)
			
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
				spss_print_common_variables(args)
			else:
				for f in args:
					print f, "Found" if os.path.exists(f) else "Not Found!"
	else:
		print "No .SAV files given"
		sys.exit(-1)
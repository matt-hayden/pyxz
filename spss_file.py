from collections import defaultdict, namedtuple
from logging import debug, info, warning, error, critical
import os.path
import cPickle as pickle

import spssaux

from console_size import redirect_terminal

### both name and factory need to have the same name for pickle
SPSS_Variable_Description = namedtuple('SPSS_Variable_Description',
	[ 'ORDER', 'LABEL', 'NAME', 'LEVEL', 'MISSING', 'FLAGS' ])
#
def vdtuple(spss_variable,
			flags = None,
			missing_values_none = (0, None, None, None),
			factory = SPSS_Variable_Description):
	"""
	Recasts SPSS variables for compactness and serialization, returning
	(order, label, name, level, missing, flags)
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
###

def spss_get_common_variables(args, 
							  name_key=lambda _: _.lower(), 
							  sort_key=lambda _: len(_[-1]), 
							  sort_reverse=True,
							  cached=True
							  ):
	"""
	Input: a list of SAV files
	Output: a list of pairs like (variable name, list of file indices that contain it)
	
	Arguments:
		name_key(name)
			By default, converts all variables to lowercase.		
	"""
	input_filenames = list(args)
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
	return var_names_by_fileorder.items() # pairs of variable name, [index of file(s) present]
#
def spss_load_variables(filename, pickle_filename = '', save=True):
	"""
	Input: one file
	Output: a list of (order, label, name, level, missing, flags)
	
	Note: SPSS v20 seems to print a lot to stdout. This function discards that output.
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
			split_vars = [_.strip() for _ in spssaux.GetDatasetInfo('SplitFile').split(',')]
			info("Split variable(s) '{}'".format(split_vars))
			for v in spssaux.VariableDict():
				flags = ''
				n = v.VariableName
				if n == filter_var:
					flags += 'F'
				if n == weight_var:
					flags += 'W'
				if n in split_vars:
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

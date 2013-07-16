
from local.console import redirect_terminal

### both name and factory need to have the same name for pickle
SPSS_Variable_Description = namedtuple('SPSS_Variable_Description',
	[ 'ORDER', 'LABEL', 'NAME', 'TYPE', 'LEVEL', 'MISSING', 'FLAGS' ])
#
def vdtuple(spss_variable,
			flags = None,
			factory = SPSS_Variable_Description,
			string_format = 'string ({})'):
	"""
	Recasts SPSS variables for compactness and serialization, returning
	(order, label, name, level, missing, flags)
	This spackles over some of the warts in SPSS python implementation and
	detects our custom variable attribute 'units'.
	"""
	my_flags = flags.upper() if flags else ''
	#
	my_level = spss_variable.VariableLevel
	if my_level == 'nominal' and spss_variable.VariableType > 0: # then string
		my_type = 'string'
		my_level = string_format.format(spss_variable.VariableType)
	else:
		my_type = 'numeric'
	# if the special attribute units is present, it's tacked on to the end of LEVEL
	if 'units' in spss_variable.Attributes and 'U' not in my_flags:
		my_flags += 'U'
	if 'U' in my_flags:
		my_units = spss_variable.Attributes.pop('units','unit').strip()
		my_level += ' ({})'.format(my_units)
	# Having no missing values is indicated by (0, None, None, None)
	my_missing = spss_variable.MissingValues2
	if my_missing == missing_values_none:
		my_missing = ''
	elif 'M' not in my_flags:
		my_flags += 'M'
	#
	return factory(spss_variable.VariableIndex,
				   spss_variable.VariableLabel,
				   spss_variable.VariableName,
				   my_type,
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
	for i, f in enumerate(input_filenames, start=1):
		print " ", i, "=", os.path.relpath(f)
		vars = spss_load_variables(f)
		for order, label, name, vtype, level, missing, flags in vars:
			if name_key:
				var_names_by_fileorder[name_key(name)].add(i)
			else:
				var_names_by_fileorder[name].add(i)
	return var_names_by_fileorder.items() # pairs of variable name, [index of file(s) present]
#
def spss_load_variables(filename,
						pickle_filename = '',
						load_cached=True,
						save_cached=True,
						factory=vdtuple):
	"""
	Input: one file
	Arguments:
		filename
		pickle_filename:	By default, filename+'.variables'
		load_cached:		Whether to try loading previously saved variable descriptions
		save_cached:		Whether to try saving variable descriptions to pickle_filename
		
	Output: a list of (order, label, name, type, level, missing, flags)
	
	Note: SPSS v20 seems to print a lot to stdout. This function discards that output.
	"""
	pickle_filename = pickle_filename or filename+'.variables'
	vars = []
	#
	if load_cached and os.path.exists(pickle_filename):
		if (os.path.getmtime(filename) <= os.path.getmtime(pickle_filename)):
			try:
				with open(pickle_filename, 'rb') as fi:
					vars = pickle.load(fi)
			except Exception as e:
				info("Loading {} failed: {} (this isn't a big deal)".format(pickle_filename, e))
			else:
				info("Using {}".format(pickle_filename))
		else:
			debug("{} exists, but not used".format(pickle_filename))
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
				vars.append(factory(v, flags=flags))
		if save_cached:
			try:
				with open(pickle_filename, 'wb') as fo:
					pickle.dump(vars, fo)
			except IOError as e:
				warning("Saving {} failed: {}".format(pickle_filename, e))
	return vars
#
def spss_get_colliding_variables(args,
								 collision_key=None,
								 ignore_vars=[],
								 **kwargs):
	"""
	Input: a list of SAV files
	Output: a list of (variable name, [ (filename, (variable name, type, missing values)), ... ])
	"""
	input_filenames = list(args)
	if isinstance(ignore_vars, basestring): ignore_vars = ignore_vars.split()
	ignore_vars = [_.lower() for _ in ignore_vars if _ != '']
	
	if collision_key:
		assert hasattr(collision_key, '__call__')
	else:
		def collision_key(vdtuple):
			comparison_type = vdtuple.LEVEL if vdtuple.TYPE == 'string' else vdtuple.TYPE
			return (vdtuple.NAME.lower(), comparison_type, vdtuple.MISSING)
	collisions_by_fileorder = defaultdict(set) # lookup file(s) for a rough variable description
	filenames_by_order = {} # lookup filename by index
	###
	for i, f in enumerate(input_filenames, start=1):
		filenames_by_order[i] = os.path.relpath(f)
		for v in spss_load_variables(f, **kwargs):
			if v.NAME.lower() in ignore_vars:
				debug("Variable {} skipped".format(v.NAME))
			else:
				collisions_by_fileorder[collision_key(v)].add(i)
	occurrences_by_property = defaultdict(list)
	for k, v in collisions_by_fileorder.items():
		occurrences_by_property[k[0].lower()].append(k)
	for varname,occurrences in occurrences_by_property.items():
		n = len(occurrences)
		if n==1: continue
		### _ is a set and not hashable here:
		#occurrences_by_file = [ (filenames_by_order[collisions_by_fileorder[_]], _) for _ in occurrences ]
		occurrences_by_file = []
		for o in occurrences:
			for prop in collisions_by_fileorder[o]:
				occurrences_by_file.append((filenames_by_order[prop], o))
		yield varname, occurrences_by_file
#
def fix_colliding_variables_to_numbers(*args, **kwargs):
	number_format = kwargs.pop('number_format', 'F2.0')
	if not (number_format.startswith('(') and number_format.endswith(')')):
		number_format = '({})'.format(number_format)
	#
	vars_by_filename = defaultdict(list)
	for varname, occurrences in spss_get_colliding_variables(*args, **kwargs):
		for filename, (_, vtype, missing) in occurrences:
			if 'string' in vtype:
				vars_by_filename[filename].append(varname)
	if kwargs.pop('one_line', False):
		return {filename:'alter type {} {}.'.format(' '.join(vs), number_format) for filename, vs in vars_by_filename.items()}
	else:
		return {filename:['alter type {} {}.'.format(v, number_format) for v in vs] for filename, vs in vars_by_filename.items()}
#
def fix_colliding_variables_to_strings(*args, **kwargs):
	string_pattern = re.compile(r'string \((\d+)\)')
	preferred_string_format = kwargs.pop('string_format', None)
	#
	def string_format_from_size(length):
		if 50 < length < 255:
			return '(A255)'
		elif length <= 1:
			return 'AMIN'
		else:
			return '(A{})'.format(length)
	#
	syntax_by_filename = defaultdict(list)
	for varname, occurrences in spss_get_colliding_variables(*args, **kwargs):
		all_numeric = False
		if preferred_string_format:
			string_format = preferred_string_format
		else:
			max_length = 0
			for filename, (_, vtype, missing) in occurrences:
				m = string_pattern.match(vtype)
				if m:
					length = int(m.groups()[0])
					if max_length < length: max_length = length
			if max_length:
				string_format = string_format_from_size(max_length)
			else:
				all_numeric = True
		if all_numeric: # TODO: maybe the user wants to alter it?
			warning("Variable {} ignored because it's apparently only found as numeric".format(varname))
		else:
			for filename, (_, vtype, missing) in occurrences:
				syntax_by_filename[filename].append('alter type {} {}.'.format(varname, string_format))
	return syntax_by_filename
					
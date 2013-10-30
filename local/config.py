import imp
import os
import os.path

def search_for_configfilename(filename):
#	dotfilename = os.path.extsep+filename
	dotfilename = filename
	assert dotfilename[1] != '.'
	while not dotfilename.startswith('.'):
		dotfilename = '.'+dotfilename
	#
	yield os.path.join(os.curdir, dotfilename)
	yield os.path.join(os.curdir, filename)
	if 'HOME' in os.environ: yield os.path.join(os.getenv('HOME'), dotfilename)
	yield os.path.join(os.path.expanduser('~'), dotfilename)
	if 'APPDATA' in os.environ: yield os.path.join(os.getenv('APPDATA'), filename)
#	try: dirname, basename = os.path.split(__file__)
#	else: yield os.path.join(dirname, filename)
#	yield os.path.join('/etc', filename)
	try:
		dirname, basename = os.path.split(__file__)
		yield os.path.join(dirname, filename)
	except:
		pass
	yield os.path.join('/etc', filename)

def load_config(filename = None,
				search_files = None,
				module_name = __package__+"_config"):
	config_file_var = module_name.upper()
	if not search_files:
		if not filename:
			filename = os.path.extsep.join((module_name, "py"))
		search_files = list(search_for_configfilename(filename))
	if config_file_var in os.environ:
		search_files.insert(0, os.getenv(config_file_var))
	if search_files:
		for fn in [ _ for _ in set(search_files) if os.path.isfile(_)]:
			with open(fn) as fi:
				return imp.load_module(module_name, fi, fn, ('.py', 'U', 1))
	return None
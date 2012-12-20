#!env python
import imp
import os
import os.path

def load_config(filename = None,
				files = None,
				module_name = 'config'):
	if filename and not files:
		files = [ os.path.join('.', '.'+filename),
				  os.path.join('.', filename),
				  os.path.join(os.getenv('HOME'), '.'+filename),
				  os.path.join(os.path.expanduser('~'), '.'+filename),
				  os.path.join('/etc', filename) ]
	search_files = filter(os.path.isfile, set(files))
	if search_files:
		with open(search_files[0]) as fi:
			loaded = imp.load_module(module_name, fi, search_files[0], ('.py', 'U', 1))
	#else:
	#	return __import__('defaultConfig')
	return loaded
if __name__ == '__main__':
	config = load_config('params.py')
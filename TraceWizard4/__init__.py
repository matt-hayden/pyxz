import imp
from itertools import ifilter
import os
import os.path

from _common import *

__all__ = [ 'TraceWizard4_File', 'MeterMaster3_MDB' ]

def load_config(filename = None,
				files = None,
				module_name = __package__+"_config"):
	config_file_var = module_name.upper()
	if not files:
		if not filename:
			filename = os.path.extsep.join((module_name, "py"))
		files = [ os.path.join('.', os.path.extsep+filename),
				  os.path.join('.', filename),
				  os.path.join(os.getenv('HOME'), os.path.extsep+filename),
				  os.path.join(os.path.expanduser('~'), os.path.extsep+filename),
				  os.path.join(os.getenv('APPDATA'), filename) if 'APPDATA' in os.environ else '',
				  os.path.join(os.path.split(__file__)[0], filename),
				  os.path.join('/etc', filename) ]
	if config_file_var in os.environ:
		files.insert(0, os.getenv(config_file_var))
	if files:
		for fn in ifilter(os.path.isfile, set(files)):
			with open(fn) as fi:
				return imp.load_module(module_name, fi, fn, ('.py', 'U', 1))
	return __import__('SomeDefaultConfig')

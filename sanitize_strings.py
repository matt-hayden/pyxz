#!env python
import os.path

"""
Remember that namedtuple has an option rename=True that numbers attributes if
they have an illegal name.
"""

def path_sanitize(arg, sep='_', valid_characters='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-._'):
	if os.path.isdir(arg):
		return arg
	dirname, basename = os.path.split(arg)
	newname = ''.join(c if c in valid_characters else sep for c in basename)
	if dirname:
		return os.path.join(dirname, newname)
	else:
		return newname
def sql_field_sanitize(arg,
					   sep='',
					   pass_brackets_through = True,
					   valid_characters='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ#$%&/:@_`{|}~',
					   pass_string_parts_through=lambda s:s.title()):
	"""
	Some programs, like SPSS, treat sep='', whereas some database exports treat
	sep='_'.
	"""
	name = arg.strip()
	bracketed = (name[0], name[-1]) == ('[', ']')
	if bracketed:
		name = name[1:-1]
	if name[0].isdigit():
		name = '@'+name # SPSS-like
	if sep:
		newname = ''.join(c if c in valid_characters else sep for c in name)
	else:
		d = ''.join(c if c in valid_characters else '_' for c in name)
		if hasattr(pass_string_parts_through, '__call__'):
			newname = sep.join(pass_string_parts_through(p) for p in d.split('_'))
		else:
			newname = d.replace('_','')
	if bracketed and pass_brackets_through:
		return '['+newname+']'
	else:
		return newname
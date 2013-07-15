#!env python
import os.path
import string

def namedtuple_field_sanitize(text, valid_characters=string.letters+string.digits+'_', sub='_'):
	"""
	Since 2.7, namedtuple also takes a rename keyword for safely handling
	invalid fields.
	"""
	stext = ''.join(_ if _ in valid_characters else sub for _ in text)
	while stext.startswith('_'):
		stext = stext[1:]
	return stext
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
					   pass_string_parts_through=None):
	"""
	Some programs, like SPSS, treat sep='', whereas some database exports treat
	sep='_'. Use pass_string_parts_through=lambda s:s.title() to send words
	through that function before joining.
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
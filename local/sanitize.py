#!env python
"""Working with strings between applications.

SQL and dispatch strings sometimes need to be massaged when passed between
applications.
"""
import os.path
import stat
import string

def namedtuple_field_sanitize(text, valid_characters=string.letters+string.digits+'_', sub='_'):
	"""Transform a string for collections.namedtuple.
	
	Since 2.7, namedtuple also takes a rename keyword for safely handling
	invalid fields.
	"""
	stext = ''.join(_ if _ in valid_characters else sub for _ in text)
	while stext.startswith('_'):
		stext = stext[1:]
	return stext
def path_sanitize(arg,
				  sep='_',
				  valid_characters='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-._',
				  mode=0):
	"""Transform a string 
	"""
	if mode:
		if stat.s_ISDIR(mode): return arg
	elif os.path.isdir(arg):
		return arg
	dirname, basename = os.path.split(arg)
	newname = ''.join(c if c in valid_characters else sep for c in basename)
	if dirname: return os.path.join(dirname, newname)
	else: return newname
def sql_field_sanitize(arg,
					   sep='',
					   pass_brackets_through=True,
					   valid_characters='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ#$%&/:@_`{|}~',
					   pass_string_parts_through=None):
	"""Transform a string into a valid SQL field name.
	
	Some programs, like SPSS, treat sep='', whereas some database exports treat
	sep='_'. Use pass_string_parts_through=lambda s:s.title() to send words
	through that function before joining.
	"""
	name = arg.strip()
	bracketed = (name[0], name[-1]) == ('[', ']')
	if bracketed:
		name = name[1:-1]
	if name[0] in string.digits:
		name = '@'+name # SPSS-like
	if sep:
		newname = ''.join(c if c in valid_characters else sep for c in name)
	else:
		d = ''.join(c if c in valid_characters else '_' for c in name)
		if hasattr(pass_string_parts_through, '__call__'):
			newname = sep.join(pass_string_parts_through(p) for p in d.split('_'))
		else:
			newname = d.replace('_','')
	if bracketed and pass_brackets_through: return '['+newname+']'
	else: return newname
def is_comment(line):
	"""Simply detect and remove comments.
	
	Useful for reading files line-by-line.
	"""
	if not line.strip(): return True
	if line.startswith('#'): return True
	if line.startswith(';'): return True
	return None
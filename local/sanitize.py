#!env python
"""
Working with strings between applications.

For Unicode to ASCII, try something like .decode('ascii', 'ignore')

SQL and dispatch strings sometimes need to be massaged when passed between
applications.
"""
import os.path
import re
import stat
import string
import shlex

def Excel_sheet_name_sanitize(text, sub=''):
	if not isinstance(text, basestring): text=str(text)
	text = text.decode('ascii', 'ignore')
	for c in ':\\/?*[]':
		if c in text: text = text.replace(c, sub)
	return text[:31]
def shell_quote(text, veto_chars="&'", split=shlex.split, strong_quote="'"):
	"""
	The argument veto_chars are characters that shlex.split passes, but are fatal to splitting
	when they're unescaped.
	"""
	if text is None or len(text) == 0: return ''
	if set(text) & set(veto_chars):
		# leave for quoting
		pass
	elif len(split(text, posix=False)) == 1: return text
	if strong_quote in text:
		text = text.replace(strong_quote, """'"'"'""") # whoa, nelly!
	return strong_quote+text+strong_quote
def namedtuple_field_sanitize(text, valid_characters=string.letters+string.digits+'_', sub='_'):
	"""Transform a string for collections.namedtuple.
	
	Since python 2.7, namedtuple also takes a rename keyword for safely handling
	invalid fields.
	"""
	stext = ''.join(c if c in valid_characters else sub for c in text)
	while stext.startswith('_'):
		stext = stext[1:]
	return stext
def path_sanitize(arg,
				  sub='_',
				  valid_characters=string.letters+string.digits+'-._@',
				  mode=0):
	"""
	Transform text so that without any special characters to sh. {}[] are considered special.
	"""
	if mode:
		if stat.s_ISDIR(mode): return arg
	elif os.path.isdir(arg):
		return arg
	dirname, basename = os.path.split(arg)
	newname = ''.join(c if c in valid_characters else sub for c in basename)
	return os.path.join(dirname, newname) if dirname else newname
def sql_field_sanitize(arg,
					   sub='',
					   pass_brackets_through=True,
					   valid_characters=string.letters+string.digits+'#$%&/:@_`{|}~',
					   pass_string_parts_through=None):
	"""Transform a string into a valid SQL field name.
	
	Some programs, like SPSS, treat sub='', whereas some database exports treat
	sub='_'. Use pass_string_parts_through=lambda s:s.title() to send words
	through that function before joining.
	"""
	name = arg.strip()
	bracketed = (name[0], name[-1]) == ('[', ']')
	if bracketed:
		name = name[1:-1]
	if name[0] in string.digits:
		name = '@'+name # SPSS-like
	if sub:
		newname = ''.join(c if c in valid_characters else sub for c in name)
	else:
		d = ''.join(c if c in valid_characters else '_' for c in name)
		if hasattr(pass_string_parts_through, '__call__'):
			newname = sub.join(pass_string_parts_through(p) for p in d.split('_'))
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
if __name__ == '__main__':
	import os
	import sys
	stderr, args = sys.stderr, sys.argv[1:]
	for pn in args or os.listdir('.'):
		if pn != path_sanitize(pn): print "mv -i", shell_quote(pn), path_sanitize(pn)
#

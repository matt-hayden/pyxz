#!env python
"""Working with CSV files.

The most common varieties of CSV are tested.
"""

import collections
import csv
import os
import os.path
import sys
from tempfile import mkstemp

from logging import debug, info, warning, error, critical

from sanitize import namedtuple_field_sanitize

class XcsvError(Exception): pass

def load_csv(fileobj, **kwargs):
	"""
	Arguments:
		iterable
		dialect		See the csv module's documentation
		header		True to import the first row as a header
					False or 0 to assume no header at all
					A string or tuple assigns it's values as header elements
		mode		'rb' for reading in binary
		skiprows	if greater than 0, 
		sanitizer	A function. Throw header names through this to catch
					illegal namedtuple fieldnames.
	"""
	if isinstance(fileobj, basestring): # assume it's a filename
		with open(fileobj, mode='rb') as fi:
			return list(gen_csv(fi, **kwargs)) # have to read the file before closing
	elif isinstance(fileobj, collections.Iterable):
		return gen_csv(fileobj, **kwargs)
	else:
		raise XcsvError('Type {} not recognized'.format(type(fileobj)))
def _sniff_header(linenum_reader, header_arg, sanitizer=namedtuple_field_sanitize):
	if header_arg:
		if isinstance(header_arg, basestring):
			headers = header_arg.split()
			skiprows = 0
		elif isinstance(header_arg, collections.Iterable):
			headers = list(header_arg)
			skiprows = 0
		elif header_arg is True:
			n, text = linenum_reader.next()
			debug("load_csv line {}: '{}'".format(n, text))
			headers = [sanitizer(f) for f in text]
			skiprows = 0
		elif type(header_arg) == int: skiprows = header_arg-1
		else: raise XcsvError("invalid header_arg {}".format(header_arg))
		if skiprows:
			for row_number in range(skiprows+1):
				debug("Skipped line {0}: '{1}'".format(*linenum_reader.next()))
			n, text = linenum_reader.next()
			debug("load_csv line {}: '{}'".format(n, text))
			headers = [sanitizer(f) for f in text]
		return headers
	else: # header in (False,0): # assume no header, i.e. from the 0th row
		return []
def gen_csv(iterable,
			dialect='excel',
			header=True,
			mode=None,
			namedtuple=True):
	linenum_reader = enumerate(csv.reader(iter(iterable), dialect=dialect), start=1)
	headers = _sniff_header(linenum_reader, header) if header else []
	if namedtuple and headers:
		Row=collections.namedtuple('Row', headers)
		num_fields = len(headers)
		for line_num, row in linenum_reader:
			debug("load_csv line {}: '{}'".format(line_num, row))
			try:
				yield Row(*row)
			except TypeError as e:
				df = len(row) - num_fields
				if df: error("Row {} has too {} fields".format(row, "many" if df > 0 else "few"))
				else: raise e
				if df < 0: row.extend([None]*(-df))
				yield Row(*row[:num_fields])
	else:
		for line_num, row in linenum_reader:
			debug("load_csv line {}: '{}'".format(line_num, row))
			yield row
#
dialect_lookup_by_ext = { 'CSV': 'excel', 'TAB': 'excel-tab', 'TSV': 'excel-tab' }

def fix_dialect(dialect):
	if not dialect.quoting:
		dialect.quoting = csv.QUOTE_MINIMAL
		info("quoting set to QUOTE_MINIMAL")
	if not dialect.escapechar:
		dialect.escapechar = "'"
		info("escapechar set to '")
def dialect_to_str(dialect):
	parts = [ ('delimiter',			dialect.delimiter.encode('unicode-escape')),
			  ('doublequote',		dialect.doublequote),
			  ('escapechar',		dialect.escapechar),
			  ('lineterminator',	dialect.lineterminator.encode('unicode-escape')),
			  ('quotechar',			dialect.quotechar),
			  ('quoting',			dialect.quoting),
			  ('skipinitialspace',	dialect.skipinitialspace)]
	try:
		parts.append(('strict', dialect.strict)) # Python 3 only?
	except: pass
	return os.linesep.join('{:>16}: {}'.format(name, value) for name, value in parts)

def passthrough(filein,
				xform,
				where=None,
				column=0,
				header_rows=0,
				header_xform=None,
				strip_header=False,
				fileout=None,
				fileout_mode='wb',
				replace=True,
				dialect=None,
				backup_suffix='.bak' if sys.platform.startswith('win') else '~'
				):
	"""
	Manipulate a CSV file while preserving its format
	
	* Add a constant-valued column
	* Transform rows via function
	* Include and exclude rows with a function
	* Strip out the header rows
	* Concatenate resultant tables into one file
	
	Arguments:
		filein, fileout, fileout_mode, replace, and backup_suffix
			If fileout isn't given:
				* The resulting table replaces filein if replace is True, and
					the original file is saved as a backup with backup_suffix
				* If replace is False, the filename of the resulting table is 
					returned
			fileout_mode='ab' allows concatentation of result tables
		xform, where, and column
			* if xform is a string, it's inserted at column
			  otherwise, xform should be a function returning the transformed
			  row, and column is ignored
			* if where is given, it should be a function returning True if a
				row isn't ignored
		dialect can specify csv internals
	Returns:
		fileout, the filename of the transformed table
	"""
	if isinstance(xform, basestring):
		def xform(row, text=xform):
			row.insert(column, text)
			return row
	if isinstance(header_xform, basestring):
		def header_xform(row, text=header_xform):
			row.insert(column, text)
			return row
	
	dirname, basename = os.path.split(filein)
	filepart, ext = os.path.splitext(basename)
	
	do_fix = False
	if not dialect:
		dialect = dialect_lookup_by_ext.get(ext.upper(), None)
		do_fix = True
		info("Some dialect properties will be adjusted")
	with open(filein, 'rb') as fi:
		if not dialect:
			tip = fi.read(1000)
			dialect = csv.Sniffer().sniff(tip)
			fi.seek(0)
		debug('Using dialect {}:'.format(dialect))
		if do_fix: fix_dialect(dialect)
		[ debug(line) for line in dialect_to_str(dialect).split(os.linesep) ]
		reader = csv.reader(fi, dialect=dialect)
		#
		fileout_obj = None
		if fileout in (None, ''):
			try:
				fh, fileout = mkstemp(dir=dirname)
				fileout_obj = os.fdopen(fh, fileout_mode or 'wb')
			except:
				fileout = filein+'.tmp'
		else:
			fileout = str(fileout)
		if not fileout_obj:
			fileout_obj = open(fileout, fileout_mode or 'wb')
		info('Writing '+fileout)
		#
		with fileout_obj as fo:
			writer = csv.writer(fo, dialect=dialect)
			if strip_header:
				[ next(reader) for hr in range(header_rows) ]
			else:
				[ writer.writerow(header_xform(next(reader))) for hr in range(header_rows) ]
			if where:
				included_count, excluded_count = 0, 0
				for row in reader:
					if where(row):
						writer.writerow(xform(row))
						included_count += 1
					else: excluded_count += 1
				info("where clause {} included {} rows and excluded {} rows".format(where, included_count, excluded_count))
			else:
				writer.writerows(xform(row) for row in reader)
	if backup_suffix and replace:
		filein_backup = filein+backup_suffix
		try:
			debug('Saving '+filein+' to '+filein_backup)
			if sys.platform.startswith('win'): # Windows only, UNIX will silently replace
				if os.path.exists(filein_backup): os.unlink(filein_backup)
			os.rename(filein, filein_backup)
		except Exception as e:
			error('File rename error: {}'.format(e))
			if os.path.exists(filein_backup) and not os.path.exists(filein):
				debug('Restoring '+filein_backup+' to '+filein)
				os.rename(filein_backup, filein)
		else:
			debug('Saving '+fileout+' to '+filein)
			os.rename(fileout, filein)
			return filein
	return fileout
#
if __name__=='__main__':
	import os.path
	import sys
	#
	if __debug__:
		import logging
		logging.basicConfig(level=logging.DEBUG)
	#
	debug("CSV can read {} dialects".format(csv.list_dialects()))
	args = sys.argv[1:]
	assert args
	for arg in args:
		with open(arg, 'rb') as fi:
			for row in gen_csv(fi, dialect='excel-tab'):
				print row
		print "As columns:"
		with open(arg, 'rb') as fi:
			for col in zip(*gen_csv(fi, dialect='excel-tab')):
				print col
#
#!env python
"""Working with CSV files.

The most common varieties of CSV are tested.
"""

import collections
import csv

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
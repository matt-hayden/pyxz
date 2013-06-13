#!env python
from collections import namedtuple
import csv
from logging import debug, info, warning, error, critical
import string

def sanitize_namedtuple_fieldnames(text, valid_characters=string.letters+string.digits+'_', sub='_'):
	stext = ''.join(_ if _ in valid_characters else sub for _ in text)
	while stext.startswith('_'):
		stext = stext[1:]
	return stext

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
		return _load_csv_gen(open(fileobj, mode='rb'), **kwargs)
	elif type(fileobj) in (file,list,tuple):
		return _load_csv_gen(fileobj, **kwargs)
	else:
		raise NotImplementedError('Type {} not recognized'.format(type(fileobj)))
def _load_csv_gen(iterable,
				  dialect='excel',
				  header=True,
				  mode=None,
				  skiprows=0,
				  sanitizer=sanitize_namedtuple_fieldnames):

	for line_num in range(skiprows):
		debug("Skipped row '{}'".format(iterable.next()))
	reader=csv.reader(iterable, dialect=dialect)
	if header is True: # load from first row
		headers = [sanitizer(_) for _ in reader.next()]
		skiprows += 1
	elif header in (False,0):
		headers = None
	else:
		if isinstance(header, basestring): header=header.split()
		headers = [sanitizer(_) for _ in header]
	if headers:
		Row=namedtuple('Row', headers)
		for line_num, row in enumerate(reader, start=1+skiprows):
			debug("load_csv line {}: '{}'".format(line_num, row))
			yield Row(*row)
	else:
		for line_num, row in enumerate(reader, start=1+skiprows):
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
		try:
			g = load_csv(arg, dialect='excel-tab')
			while True:
				g.next()
		except Exception as e:
			print "Reading", arg, "failed"
			raise e
#			exc_type, exc_obj, exc_tb = sys.exc_info()
#			dirname, basename = os.path.split(exc_tb.tb_frame.f_code.co_filename)
#			print '  File: "{}", line {}'.format(basename, exc_tb.tb_lineno)
#			print type(e).__name__+":", e.message
	
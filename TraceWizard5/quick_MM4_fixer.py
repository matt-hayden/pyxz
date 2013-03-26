import fileinput
from logging import debug, info, warning, error, critical
import os, os.path

from SelfNamedZipFile import SelfNamedZipFile

"""
Note that CRLF are converted to LF.
"""

max_header_rows_to_parse=26
max_rows_total=max_header_rows_to_parse+129600

def bug_filter(filepath):
	"""
	Generator, yielding filtered rows.
	"""
#	end_of_header = "DateTimeStamp,RateData\n"
	dirname, basename = os.path.split(filepath)
	filepart, ext = os.path.splitext(basename)
	with SelfNamedZipFile(filepath, default_extensions = ['.CSV']) if ext.upper() in ['.ZIP'] else open(filepath) as fi:
		header = [ fi.next() for r in range(1,max_header_rows_to_parse) ]
		num_tokens = 0
		for row in header:
#			if row == end_of_header:
#				yield row
#				continue
#			key, value = [ x.strip() for x in row.split(',', 1) ]
			key, value = row.split(',', 1)
			ukey, newvalue, token = key.upper(), value, False
			if ukey == 'BEGINREADING':
				newvalue = value.replace('"','').replace(',','')
				token = True
			elif ukey == 'ENDREADING':
				newvalue = value.replace('"','').replace(',','')
				token = True
#			elif ukey == 'CONVFACTOR':
#				newvalue = value.replace('"','').replace(',','.')
#				token = True
			if token and (value != newvalue):
				num_tokens += 1
				debug("Replaced {} in {}".format(key, filepath))
				yield ','.join((key,newvalue)) 
			else:
				yield row
		if num_tokens:
			info("{} replacements in {}".format(num_tokens, filepath))
		else:
			debug("No change to {}".format(filepath))
		for x in xrange(max_rows_total):
			yield fi.next() # a stopiteration here quits the generator
def apply_filter(filepath, backup='.bak', filter_gen=bug_filter):
	dirname, basename = os.path.split(filepath)
	filepart, ext = os.path.splitext(basename)
	#
	if ext.upper() in ['.ZIP']:
		#
		working_filepath = os.path.join(dirname, filepart)
		filepart, ext = os.path.splitext(working_filepath)
		if ext.upper() not in ['.CSV']:
			working_filepath = filepart+'.CSV'
		#
		if os.path.exists(working_filepath):
			critical("File '{}' already extracted to '{}', and may have already been processed".format(filepath, working_filepath))
			return False
		with open(working_filepath, 'wb') as fo:
			fo.writelines(bug_filter(filepath))
		return True
	else:
		working_filepath, backup_filepath = filepath+'.new', filepath+(backup or '.bak')
		#
		if os.path.exists(backup_filepath):
			critical("File '{}' already has a backup version '{}', and may have already been processed".format(filepath, backup_filepath))
			return False
		with open(working_filepath, 'wb') as fo:
			fo.writelines(bug_filter(filepath))
		os.rename(filepath, backup_filepath)
		os.rename(working_filepath, filepath)
		return True

if __name__ == '__main__':
	import logging
	import sys
	
	from myglob import myglob
	
	logging.basicConfig(level=logging.DEBUG)
	failures = []
	for arg in sys.argv[1:] or myglob('*.CSV'):
		if not apply_filter(arg):
			failures.append(arg)
	if failures:
		print len(failures), "failures:"
		for f in failures:
			print "\t", f
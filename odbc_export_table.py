from contextlib import closing
import csv
import os.path
import sys

import pyodbc as odbc

from path_sanitize import path_sanitize

def get_connection_string(**kwargs):
	exclusive = 1 if kwargs.pop('exclusive',None) else 0
	read_only = 1 if kwargs.pop('read_only',None) else 0
	database_filename = os.path.abspath(os.path.normpath(kwargs['database_filename']))
	parts = ('DRIVER={Microsoft Access Driver (*.mdb, *.accdb)}',
			 'DBQ={}'.format(database_filename),
			 'ReadOnly={}'.format(read_only) ) 
	return ';'.join(parts)
def export_table(*args, **kwargs):
	"""
	export_table(db, tbl, csv) dumps the contents of [db]![tbl] to the csv file
	export_table(db, tbl) dumps the contents of [db]![tbl] to the screen
	
	Understood keyword arguments:
		One of the following:
			database_filename (can be relative)
			connection_string (passed to pyodbc.connect)
			connection object (need not be via pyodbc)
			
		One of the following:
			table_name
			sql
		
		output = a filename or file object, by default screen
		Modifiers for output:
			append = False to overwrite existing files
			overwrite = True to allow overwriting
	"""
	l = len(args)
	if l >= 3:
		kwargs['database_filename'], kwargs['table_name'], kwargs['output'] = args
		extra_non_keyword_args = args[3:]
	if l == 2:
		kwargs['database_filename'], kwargs['table_name'] = args
	#
	input_found = os.path.isfile(kwargs['database_filename'])
	#
	### output can be an open file or a filename, but not an object returned by
	### csv.writer()
	output = kwargs.pop('output', sys.stdout)
	if not isinstance(output, file): # open a filename, possibly deriving it
		if os.path.isdir(output):
			dirname, basename = os.path.split(kwargs['database_filename'])
			filepart, ext = os.path.splitext(basename)
			output_filename = os.path.join(output, path_sanitize(filepart+'!'+kwargs['table_name']+'.CSV'))
		else:
			output_filename = output
		output_found = os.path.exists(output_filename)
		if output_found and not kwargs.pop('overwrite', False):
			raise IOError("Refusing to overwrite '{}'".format(output))
		mode = 'ab' if kwargs.pop('append', False) else 'wb'
		output = open(output_filename, mode)
	writer = csv.writer(output)
	#
	connection = kwargs.pop('connection', None)
	if not connection:
		connection_string = kwargs.pop('connection_string', get_connection_string(read_only=True, **kwargs))
		connection = odbc.connect(connection_string)
	sql = kwargs.pop('sql', 'select * from {}'.format(kwargs.pop('table_name')))
	with closing(connection.cursor()) as cursor:
		cursor.execute(sql)
		headers = [ _[0] for _ in cursor.description ]
		writer.writerow(headers)
		writer.writerows(row for row in cursor)
#
if __name__ == '__main__':
	export_table(*sys.argv[1:])
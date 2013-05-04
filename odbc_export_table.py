from contextlib import closing
import csv
import os.path
import sys

import pyodbc as odbc

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
	if len(args) == 2:
		kwargs['database_filename'], kwargs['table_name'] = args
	#
	assert os.path.isfile(kwargs['database_filename'])
	#
	output = kwargs.pop('output', sys.stdout)
	if isinstance(output, file):
		writer = csv.writer(output)
	#elif os.path.isdir(output):
	#
	else:
		#if (not kwargs.pop('overwrite', False) and os.path.exists(output)):
		#
		writer = csv.writer(open(output,'ab' if kwargs.pop('append', False) else 'wb'))
	#
	if 'connection' in kwargs:
		connection = kwargs.pop('connection')
	else:
		connection_string = kwargs.pop('connection_string', get_connection_string(read_only=True, **kwargs))
		connection = odbc.connect(connection_string)
	sql = kwargs.pop('sql', 'select * from {}'.format(kwargs.pop('table_name')))
	with closing(connection.cursor()) as cursor:
		cursor.execute(sql)
		headers = [ _[0] for _ in cursor.description ]
		writer.writerow(headers)
		writer.writerows(row for row in cursor)
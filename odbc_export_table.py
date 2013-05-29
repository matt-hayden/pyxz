
from collections import namedtuple
from contextlib import closing
import csv
import os.path
import sys

from pyodbc import connect

from sanitize_strings import *
	
def get_connection_string(*args, **kwargs):
	l = len(args)
	if l == 1:
		database_filename = kwargs.pop('database_filename', args[0])
	else:
		database_filename = kwargs.pop('database_filename')
	#
	exclusive = 1 if kwargs.pop('exclusive',None) else 0
	read_only = 1 if kwargs.pop('read_only',None) else 0
	#
	#database_filename = os.path.abspath(os.path.normpath(database_filename))
	database_filename = os.path.abspath(database_filename)
	#
	parts = ('DRIVER={Microsoft Access Driver (*.mdb, *.accdb)}',
			 'DBQ={}'.format(database_filename),
			 'ReadOnly={}'.format(read_only) ) 
	return ';'.join(parts)
def get_table(*args, **kwargs):
	"""
	Understood keyword arguments:
		One of the following:
			database_filename (can be relative)
			connection_string (passed to pyodbc.connect)
			connection object (need not be via pyodbc)
			
		One of the following:
			table_name
			sql, possibly with a 'parameters' argument
	"""
	l = len(args)
	if l == 2:
		kwargs['database_filename'], kwargs['table_name'] = args
	elif l == 1:
		kwargs['database_filename'] = args[0]
	connection = kwargs.pop('connection', None)
	if not connection:
		connection_string = kwargs.pop('connection_string', get_connection_string(read_only=True, **kwargs))
		connection = connect(connection_string)
	if 'sql' in kwargs:
		sql = kwargs.pop('sql')
	elif 'table_name' in kwargs:
		sql = 'select * from [{}]'.format(kwargs.pop('table_name'))
	with closing(connection.cursor()) as cursor:
		if 'parameters' in kwargs:
			cursor.execute(sql, kwargs.pop('parameters'))
		else:
			cursor.execute(sql)
		# the row factory is built here
		headers = [ sql_field_sanitize(_[0], pass_brackets_through=False) for _ in cursor.description ]
		Row=namedtuple('Row', headers)
		table = [ Row(*_) for _ in cursor ]
	return table
#
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
			sql, possibly with a 'parameters' argument
		
		output = a filename or file object, by default screen
		Modifiers for output:
			append = False to overwrite existing files
			overwrite = True to allow overwriting
	"""
	l = len(args)
	if l >= 3:
		kwargs['database_filename'], kwargs['table_name'], kwargs['output'] = args
		extra_non_keyword_args = args[3:]
	elif l == 2:
		kwargs['database_filename'], kwargs['table_name'] = args
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
	table = get_table(**kwargs)
	with output as fo:
		writer = csv.writer(fo)
		writer.writerow(table[0]._fields)
		writer.writerows(table)
#
if __name__ == '__main__':
	export_table(*sys.argv[1:])
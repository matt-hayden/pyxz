#!env python
"""
Usage:
	$me database					List all recognized tables
	$me tablename database1 ...		Export all tables named tablename from many files
"""
from MDB import debug, info, warning, error, critical
from database_file import pyodbc_MDB

from local.xnp import *

class pyodbc_MDB_np(pyodbc_MDB):
	"""
	Currently, numpy support only works with the pyODBC driver. Any other
	driver needs to support the cursor.description members so that fields can be
	translated from the database into numpy.
	"""
	def generate_table(self, *args, **kwargs):
		"""
		This is a numpy extension to the normal MDB_File interface.
		
		Optional keyword arguments:
			sql or SQL: syntax to execute
			cursor: cursor object to re-use
			parameters: a tuple that replaces '?' in SQL syntax
			named: returned iterable is a namedtuple based on field names (This
				is not supported by all drivers)
		"""
		with self.execute(*args, **kwargs) as cursor:
			my_dtypes = np.dtype([np_dtype_from_ODBC_desc(_) for _ in cursor.description])
			# fromiter doesn't like a naked cursor. Wrap each row in a tuple:
			table = np.fromiter((tuple(_) for _ in cursor), dtype=my_dtypes, count=cursor.rowcount or -1)
		return table
	def export_table(self, table_name, filename):
		np.save(filename, self.generate_table(table_name))
#
def main(tablename, input_filename, output_filename=None):
	filepart, ext = os.path.splitext(input_filename)
	if not output_filename:
		output_filename = os.path.extsep.join((filepart,table_name))
	if os.path.exists(output_filename+'.npy'):
#		print >>sys.stderr, "Refusing to overwrite", output_filename+'.npy'
		error("Refusing to overwrite"+output_filename+'.npy')
		return 1
	with pyodbc_MDB_np(input_filename, read_only=True) as db:
		db.export_table(table_name, output_filename)
	return 0
#
if __name__ == '__main__':
#	import cProfile
#	import logging
	import os.path
	import sys
	
	import local.console.size
	from local.xglob import glob

	args = sys.argv[1:]
	nargs = len(args)
	if nargs == 0:
		print __doc__
	elif nargs == 1: # merely list tables in a single file
		input_filename = args[0]
		with pyodbc_MDB_np(input_filename, read_only=True) as db:
			tns = db.table_names
			if tns:
				print "Tables found in {}:".format(input_filename)
				print local.console.size.to_columns(tns)
				print
			else:
				print "No tables recognized in "+input_filename
	else: # pull the same-named table from many files
		for filename in args[1:]:
			main(args[0], filename)
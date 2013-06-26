#!env python
from MDB import debug, info, warning, error, critical
from database_file import pyodbc_MDB

from local.xnp import *
#
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
MDB_File = pyodbc_MDB_np # a non-numpy MDB_File also exists in MDB_File
#
if __name__ == '__main__':
	import cProfile
	import logging
	import os.path
	import sys
	
	from local.xglob import glob
	#
	if __debug__:	logging.basicConfig(level=logging.DEBUG)
	else:			logging.basicConfig(level=logging.WARNING)
	#
	args = sys.argv[1:]
	nargs = len(args)
	if nargs >= 2:
		table_name = args.pop()
		input_files = args
		for input_filename in input_files:
			filepart, ext = os.path.splitext(input_filename)
#			output_filename = os.path.extsep.join((filepart,table_name,'NPY'))
			output_filename = os.path.extsep.join((filepart,table_name))
#			if os.path.exists(output_filename):
			if os.path.exists(output_filename+'.npy'):
				print >>sys.stderr, "Refusing to overwrite", output_filename+'.npy'
			else:
				with MDB_File(input_filename, read_only=True) as db:
					db.export_table(table_name, output_filename)
	else:
		input_files = args or glob('*.MDB', '*.accdb')
		assert input_files
		for input_filename in input_files:
				with MDB_File(input_filename, read_only=True) as db:
					print "Tables found in {}".format(input_filename)
					for t in db.table_names:
						print t
					print
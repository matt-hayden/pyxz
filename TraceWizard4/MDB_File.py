#!env python
"""
Reader for MS Access single-file databases, typically .MDB. This may work with
.accdb files as well. Currently, the only systems that can handle these files
are Windows-based. All testing has been done on Windows XP using pyodbc. 
Note that there are at least four maintained database drivers:
* adobdbapi		Comes with pywin32, uses ADO calls.
* ceODBC		(untested)
* odbc			(untested) 
* pyodbc		Wraps the ODBC facility on Windows.
"""

from collections import namedtuple
from contextlib import closing
from logging import debug, info, warning, error, critical
import sys

try:
	import pyodbc as import_driver
except:
	debug("Driver pyodbc not available")
	try:
		import adodbapi as import_driver
	except:
		debug("Driver adodbapi not available")

if import_driver:
	info("Module using driver", import_driver.__name__)
else:
	if sys.platform == 'win32':
		raise NotImplementedError("Install a valid database driver")
	else:
		raise NotImplementedError("Not implemented on " + sys.platform)
#
class MDB_Error(Exception):
	pass
#
def MDB_File(filename, driver_name = None):
	"""
	Convenience function to determine available database drivers.
	"""
	driver_name = driver_name or import_driver.__name__
	info("MDB looking for driver %s" % driver_name)
	if driver_name == 'pyodbc':
		return pyodbc_MDB(filename)
	elif driver_name.startswith('ce'):
		return MDB_Base(filename)
	elif driver_name == 'odbc':
		return odbc_MDB(filename)
	elif driver_name.startswith('ado'):
		return adodbapi_MDB(filename)
class MDB_Base:
	"""
	"""
	driver_name = import_driver.__name__
	MSysObjects_Row = namedtuple('TableDef', 'Connect Database DateCreate DateUpdate Flags ForeignName ID Lv LvExtra LvModule LvProp Name Owner ParentID RmtInfoLong RmtInfoShort Type')
	#
	def __init__(self, data):
		self.open_file(data)
	@staticmethod
	def connection_string_for_file(filename):
		"""
		Seems to be fine for all ODBC connectors.
		"""
		return ';'.join(
			["Driver={Microsoft Access Driver (*.mdb)}",
			 "Dbq="+filename])
	def open_file(self, filename):
		cstring = self.connection_string_for_file(filename)
		self.con = import_driver.connect(cstring)
	def get_table_defs(self):
		"""
		Note that this may or may not be accurate. Not all database drivers support listing tables.
		* ceODBC provides a cursor from Connection.tables
		* pyodbc provides method Cursor.tables
		The generic approach assumes MSysObjects is readable.
		"""
		try:
			with closing(self.con.cursor()) as cur:
				cur.execute("select * from MSysObjects where Type=1")
				return [ MSysObject_Row(*r) for r in cur.fetchall() ]
		except:
			info("Table defs not available")
			return None
	@property
	def table_names(self):
		td = self.get_table_defs()
		if td:
			return [ t.table_name for t in td ]
		else:
			return None
	def generate_table(self, table_name):
		return self.generate_query(sql="select * from [%s]" % table_name)
	def generate_query(self, sql):
		with closing(self.con.cursor()) as cur:
			cur.execute(sql)
			return list(cur.fetchall())
class odbc_MDB(MDB_Base):
	"""
	Example subclass of MDB_Base.
	"""
	def open_file(self, filename):
		"""
		Uses a different call to open a connection.
		"""
		cstring = self.connection_string_for_file(filename)
		self.con = import_driver.odbc(cstring)
class adodbapi_MDB(MDB_Base):
	"""
	Example subclass of MDB_Base.
	"""
	@staticmethod
	def connection_string_for_file(filename):
		"""
		ADO uses a different connection string than ODBC.
		"""
		return ';'.join(
			["Provider=Microsoft.Jet.OLEDB.4.0",
			 "Data Source="+filename])
	def get_field_names_for_cursor(self, cur):
		return [ f[0] for f in cur.description ]
class pyodbc_MDB(MDB_Base):
	"""
	Example subclass of MDB_Base.
	"""
	pyodbc_TableDef = namedtuple('TableDef', 'table_cat table_schem table_name table_type remarks')
	# for some reason, pyodbc gives an extra field:
	pyodbc_ColumnDef = namedtuple('ColumnDef', 'table_cat table_schem table_name column_name data_type type_name column_size buffer_length decimal_digits num_prec_radix nullable remarks column_def sql_data_type sql_datetime_sub char_octet_length ordinal_position is_nullable X1')
	def get_table_defs(self):
		cur = self.con.cursor()
		return [ self.pyodbc_TableDef(*t) for t in cur.tables(tableType='TABLE').fetchall() ]
	def get_field_defs_for_cursor(self, cur):
		return [ self.pyodbc_ColumnDef(*f) for f in cur.columns().fetchall() ]
	def get_field_names_for_cursor(self, cur):
		return [ f.column_name for f in self.get_field_defs_for_cursor(cur) ]
#
if __name__ == '__main__':
	import logging
	import os.path
	#
	logging.basicConfig(level=logging.INFO)
	#
	#desktop=os.path.expandvars('%UserProfile%\Desktop')
	tempdir=os.path.expandvars('%TEMP%\example-traces')
	fn = os.path.join(tempdir, '67096.MDB')
	m = MDB_File(fn)
	print "table_defs:", m.get_table_defs()
	print "table_names:", m.table_names
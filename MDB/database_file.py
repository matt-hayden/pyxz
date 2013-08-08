#!env python
"""
Wrapper for MS Access single-file databases, typically .MDB. This may work with
.accdb files as well. Currently, the only systems that can handle these files
are Windows-based. All testing has been done on Windows using pyodbc. 

Note that there are at least four maintained database drivers:
* adobdbapi		Comes with pywin32, uses ADO calls.
* ceODBC		(untested)
* odbc			(untested) 
* pyodbc		Wraps the ODBC facility on Windows.
"""
from MDB import debug, info, warning, error, critical

from collections import namedtuple
from contextlib import closing
import os
import sys

from local.sanitize import sql_field_sanitize

import_driver = None
try:
	import pyodbc as import_driver
	driver_name = import_driver.__name__
except:
	warning("Driver pyodbc not available")
	try:
		import adodbapi as import_driver
	except:
		warning("Driver adodbapi not available")

if import_driver:
	info("Module using driver "+import_driver.__name__)
else:
	if sys.platform == 'win32':
		raise NotImplementedError("Install a valid database driver")
	else:
		raise NotImplementedError("Not implemented on " + sys.platform)
#
class MDB_Error(Exception):
	pass
#
def MDB_File(filename, **kwargs):
	"""
	Convenience function for opening a MDB or ACCDB file using whatever driver
	might be available.
	
	Arguments:
		filename
	"""
	assert os.path.exists(filename)
	driver_name = kwargs.pop('driver_name', import_driver.__name__)
	info("MDB looking for driver "+driver_name)
	if driver_name == 'pyodbc':
		return pyodbc_MDB(filename, **kwargs)
	elif driver_name.startswith('ce'):
		return MDB_Base(filename, **kwargs)
	elif driver_name == 'odbc':
		return odbc_MDB(filename, **kwargs)
	elif driver_name.startswith('ado'):
		return adodbapi_MDB(filename, **kwargs)
def get_table(filename, table_name, **kwargs):
	"""
	Convenience function for returning one table in one foul swoop.
	"""
	with MDB_File(fn, read_only=True) as db:
		table = db.generate_table(table_name, **kwargs)
		return list(table)
#
class MDB_Base(object):
	"""
	The following methods and properties are available regardless of import
	driver.
	"""
	default_ID_field_type = 'AUTOINCREMENT(1, 1)'
	driver_name = import_driver.__name__
	MSysObjects_Row = namedtuple('TableDef', 'Connect Database DateCreate DateUpdate Flags ForeignName ID Lv LvExtra LvModule LvProp Name Owner ParentID RmtInfoLong RmtInfoShort Type')
	#
	def __init__(self, data, **kwargs):
		self.no_commit = kwargs.pop('no_commit', True)
		if not self.no_commit:
			kwargs['read_only'] = False
		self.open_file(data, **kwargs)
	def __enter__(self):
		return self
	def __exit__(self, error_type, error_value, traceback):
		if not self.no_commit:
			self.commit()
	@staticmethod
	def connection_string_for_file(*args, **kwargs):
		"""
		Seems to be fine for all ODBC connectors. DBAPI suggests keyword args
		user and password for the connect() method.
		
		Arguments:
			filename
		Optional arguments:
			exclusive
			read_only
		"""
		l = len(args)
		if l == 1: (database_filename,) = args
		else: database_filename = kwargs.pop('database_filename')
		#
		#database_filename = os.path.abspath(os.path.normpath(database_filename))
		database_filename = os.path.abspath(database_filename)
		#
		parts = ('DRIVER={Microsoft Access Driver (*.mdb, *.accdb)}',
				 'DBQ='+database_filename)
		# ReadOnly=0 apparently also means ReadOnly
		if kwargs.pop('read_only', False): parts += ('ReadOnly=1',)
		return ';'.join(parts)
	def open_file(self, filename, **kwargs):
		self.connection = kwargs.pop('connection', None)
		if not self.connection:
			self.connection_string = kwargs.pop('connection_string', None) \
				or self.connection_string_for_file(filename, **kwargs)
			debug("Opening {} with '{}'".format(filename, self.connection_string))
			self.connection = import_driver.connect(self.connection_string)
	def get_table_defs(self):
		"""
		Assumes MSysObjects is readable.
		
		Note that this may or may not be accurate. Not all database drivers
		support listing tables.
		* ceODBC provides a cursor from Connection.tables
		* pyodbc provides method Cursor.tables
		"""
		try:
#			with self.cursor() as cur:
#				cur.execute("select * from MSysObjects where Type=1")
			with self.execute("select * from MSysObjects where Type=1") as cur:
				return [ MSysObjects_Row(*r) for r in cur ]
		except:
			error("Table defs not available for "+self.driver_name)
			return None
	@property
	def table_names(self):
		return [_.table_name for _ in self.get_table_defs() ]
	
	def execute(self, *args, **kwargs):
		"""
		Wrapper around cursor.execute() that returns a context-aware object.
		"""
		try:
			cursor = self.connection.execute(*args)
		except Exception as e:
			critical("execute{} failed!".format(args))
			raise e
		else:
			debug("execute{}".format(args))
		return closing(cursor)
	def generate_table(self, *args, **kwargs):
		"""
		Input:
			A sql statement and some tables to run it on. If multiple tables
			are given, then results are concatenated (regardless of whether
			columns match up or have the same number of elements).
		Output:
			A Row object that is a namedtuple. The memebers may not exactly
			match the query result if the field names contain invalid
			characters.
		Optional keyword arguments:
			sql or SQL: syntax to execute
		"""
		if 'sql' in kwargs: sql = kwargs.pop('sql')
		elif is_sql(args[0]): sql, args = args[0], args[1:]
		else: sql = 'select * from {table_name};' # see below
		
		table_names = [sanitize_table_name(arg) for arg in args]
		
		if table_names: sqls = [sql.format(table_name=tn) for tn in table_names]
		else: sqls = [sql]
		
		for sql in sqls:
			with self.execute(sql) as cursor:
				try:
					Row=namedtuple('Row', self.get_field_names_for_cursor(cursor) )
					for _ in cursor:
						yield Row(*_)
				except Exception as e:
					info("generate_table() will not return namedtuple: {}".format(e))
					for _ in cursor:
						yield _
		else: raise MDB_Error("generate_table() received invalid SQL statement: '{}'".format(sql)
	def cursor(self, *args, **kwargs):
		return closing(self.connection.cursor(*args, **kwargs))
	def commit(self, *args, **kwargs):
		self.connection.commit(*args, **kwargs)
	def create_table(self,
					 table_name,
					 fields,
					 field_types = [],
					 **kwargs):
		if isinstance(fields, basestring):
			fields = fields.split()
		nfields = len(fields)
		if isinstance(field_types, basestring):
			field_types = field_types.split()
		if field_types:
			if len(field_types) != nfields:
				raise MDB_Error("Number of field names and number of field types do not match!")
			for i, ftype in enumerate(field_types):
				if not isinstance(ftype, basestring):
					field_types[i] = '{}({})'.format(*ftype)
		else:
			field_types = ('VARCHAR(255)',)*nfields
		field_def = ', '.join(n+' '+t for n, t in zip(fields, field_types))
		sql = 'CREATE TABLE {0} ({1});'.format(table_name, field_def)
		debug("create_table(sql = '{}')".format(sql))
		try:
			with self.cursor() as cursor:
				cursor.execute(sql)
				cursor.commit()
		except Exception as e:
			error("create_table({}, sql={}) failed: {}".format(table_name, sql, e))
			raise e
	def get_create_coroutine(self,
							 table_name,
							 fields,
							 field_types = [],
							 **kwargs):
		ID_name = kwargs.pop('ID', '')
		if isinstance(fields, basestring):
			fields = fields.split()
		if isinstance(field_types, basestring):
			field_types = field_types.split()
		#
		create_fields = fields
		if ID_name:
			create_fields = [ID_name]+fields
			field_types.insert(0, self.default_ID_field_type)
		try:
			self.create_table(table_name, create_fields, field_types)
		except Exception as e:
			try:
				errno, message = e
				if errno in ('42S01',): # table already exists
					error("get_create_coroutine(): table {} already exists".format(table_name))
				else: raise e
			except:
				raise e
		return self.get_append_coroutine(table_name, fields, **kwargs)
	def get_append_coroutine(self,
							 table_name,
							 fields,
							 row_limit=10**7,
							 **kwargs):
		if isinstance(fields, basestring):
			fields = fields.split()
		nfields = len(fields)
		append_sql = 'INSERT INTO {0}({1}) VALUES ({2});'.format(table_name,
			', '.join(fields),
			','.join(('?',)*nfields))
		debug("get_append_coroutine(sql = '{}')".format(append_sql))
		def coroutine(sql):
			with self.cursor() as cursor:
				try:
					for iteration in xrange(row_limit):
						content = (yield iteration)
						if content:
							debug("Iteration {}: {}".format(iteration, content))
#							if len(content) != nfields:
#								print "Content has {} fields, expected {}".format(len(content), nfields)
#								print "Content: {}".format(content)
							cursor.execute(sql, content)
						else:
							info("Skipped iteration {}: no data".format(iteration))
					raise NotImplementedError("{} rows exceeded".format(iteration))
				except GeneratorExit:
					debug("Iteration {} completed: {}".format(iteration-1, content))
					cursor.commit()
		c = coroutine(sql=append_sql)
		c.next() # coroutine
		return c
class odbc_MDB(MDB_Base):
	"""
	Example subclass of MDB_Base.
	"""
	def open_file(self, filename):
		"""
		Uses a different call to open a connection.
		"""
		cstring = self.connection_string_for_file(filename)
		self.connection = import_driver.odbc(cstring)
class adodbapi_MDB(MDB_Base):
	"""
	Example subclass of MDB_Base.
	"""
	@staticmethod
	def connection_string_for_file(filename, **kwargs):
		"""
		ADO uses a different connection string than ODBC.
		"""
		#
		parts = ["Provider=Microsoft.Jet.OLEDB.4.0",
				 "Data Source="+filename]
		return ';'.join(parts)
	def get_field_names_for_cursor(self, cur, sanitizer=sql_field_sanitize):
#		return [ f.column_name for f in self.get_field_defs_for_cursor(cur) ]
		if hasattr(sanitizer, '__call__'):
			return [ sanitizer(_.column_name, pass_brackets_through=False) for _ in cur.description ]
		else:
			return [ _.column_name for _ in cur.description ]
class pyodbc_MDB(MDB_Base):
	"""
	Example subclass of MDB_Base.
	"""
	#
	pyodbc_TableDef = namedtuple('TableDef', 'table_cat table_schem table_name table_type remarks')
	# for some reason, pyodbc gives an extra field:
	pyodbc_ColumnDef = namedtuple('ColumnDef', 'table_cat table_schem table_name column_name data_type type_name column_size buffer_length decimal_digits num_prec_radix nullable remarks column_def sql_data_type sql_datetime_sub char_octet_length ordinal_position is_nullable field_19')
	pyodbc_CursorDescription = namedtuple('CursorDescription', 'name type_code display_size internal_size precision scale null_ok')
	#
	def get_table_defs(self):
		with self.cursor() as cur:
			return [ self.pyodbc_TableDef(*t) for t in cur.tables(tableType='TABLE').fetchall() ]
	def get_field_defs_for_cursor(self, cur):
#		return [ self.pyodbc_ColumnDef(*f) for f in cur.columns().fetchall() ]
		return [ self.pyodbc_CursorDescription(*_) for _ in cur.description ]
	def get_field_names_for_cursor(self, cur, sanitizer=sql_field_sanitize):
		if hasattr(sanitizer, '__call__'):
			return [ sanitizer(_.name, pass_brackets_through=False) for _ in self.get_field_defs_for_cursor(cur) ]
		else:
			return [ _.column_name for _ in self.get_field_defs_for_cursor(cur) ]
	def execute(self, *args, **kwargs):
		"""
		Wrapper around execute() that can take a table name or sql as a
		keyword argument. This driver has some extra functionality than it's
		parent.
		"""
		try:
			return super(pyodbc_MDB, self).execute(*args, **kwargs)
		except Exception as e:
			critical(e)
			raise self._parse_error(e)
	@staticmethod
	def _parse_error(e):
		if e[0] in ('42000', 42000):
			error("System and Hidden objects may need to be enabled within MS Access")
			return NotImplementedError("System and Hidden objects may need to be enabled within MS Access")
		else:
			return e
#
#!env python

from collections import namedtuple
from logging import debug, info, warning, error, critical
import os.path

from odbc_wrapper import odbc, odbc_wrapper

class MDB_file(odbc_wrapper):
	"""
	A wrapper around the pretty good python database API.
	Enables certain custom adaptors.
	>>> db = MDB_file('foo.mdb')
	
	There are two ways to populate a table:
	
	A coroutine to which you send() complete rows: (this one creates the table first)
	>>> co = db.get_create_coroutine('MyTable', ['Name'],['TEXT'], ID='ID')
	>>> alice_id = co.send(['Alice'])
	>>> another_id = co.send(['Ben'])
	>>> another_id = co.send(['Gadot'])

	The executemany method: (possibly accelerated, depending on the driver)
	>>> cur = db.executemany('insert into MyTable(Name) values (?);', [ ('Eddie',), ('Zekie',) ])
	
	>>> print "Tables: "+' '.join(db.table_names)
	Tables: MyTable
	
	>>> for row in db.generate_table('select Name from MyTable order by ID'): print row
	Row(Name=u'Alice')
	Row(Name=u'Ben')
	Row(Name=u'Gadot')
	Row(Name=u'Eddie')
	Row(Name=u'Zekie')
	"""
	default_ID_field_type = 'AUTOINCREMENT(1, 1)'
	default_field_type = 'VARCHAR(255)'
	
	MSysObjects_Row = namedtuple('TableDef', 'Connect Database DateCreate DateUpdate Flags ForeignName ID Lv LvExtra LvModule LvProp Name Owner ParentID RmtInfoLong RmtInfoShort Type')
	
	@staticmethod
	def get_connection_string_for_file(*args, **kwargs):
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
		if l == 1:	(database_filename,) = args
		else:		database_filename = kwargs.pop('database_filename')
		#
		#database_filename = os.path.abspath(os.path.normpath(database_filename))
		database_filename = os.path.abspath(database_filename)
		#
		parts = ('DRIVER={Microsoft Access Driver (*.mdb, *.accdb)}',
				 'DBQ='+database_filename)
		# ReadOnly=0 apparently also means ReadOnly
		if kwargs.pop('read_only', False): parts += ('ReadOnly=1',)
		return ';'.join(parts)
	def __init__(self, data, **kwargs):
		self.no_commit = kwargs.pop('no_commit', True)
		self.open_file(data, **kwargs)
	def open_file(self, filename, **kwargs):
		self.connection_string = self.get_connection_string_for_file(filename, **kwargs)
		debug("Opening {} with '{}'".format(filename, self.connection_string))
		self.connection = odbc.connect(self.connection_string)
		
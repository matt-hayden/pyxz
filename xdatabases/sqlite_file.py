#!env python

import sqlite3 as sqlite

from xdatabases import _xdatabase_base

class sqlite_file(_xdatabase_base):
	"""
	A wrapper around the pretty good python database API.
	Enables certain custom adaptors.
	>>> db = sqlite_file('foo.db')
	
	There are two ways to populate a table:
	
	A coroutine to which you send() complete rows: (this one creates the table first)
	>>> co = db.get_create_coroutine('MyTable', ['Name'],['TEXT'], ID='ID')
	>>> alice_id = co.send(['Alice'])
	>>> another_id = co.send(['Ben'])
	>>> another_id = co.send(['Gadot'])

	The executemany method: (possibly accelerated, depending on the driver)
	>>> cur = db.executemany('insert into MyTable(Name) values (?);', [ ('Eddie',), ('Zekie',) ])
	
	>>> print "Tables: "+' '.join(db.table_names)
	Tables: MyTable sqlite_sequence
	
	>>> for row in db.generate_table('select Name from MyTable order by ID'): print row
	Row(Name=u'Alice')
	Row(Name=u'Ben')
	Row(Name=u'Gadot')
	Row(Name=u'Eddie')
	Row(Name=u'Zekie')
	"""
	default_ID_field_type = 'INTEGER PRIMARY KEY AUTOINCREMENT'
	default_field_type = 'TEXT'
	#
	def __init__(self, data=':memory:', **kwargs):
		self.no_commit = kwargs.pop('no_commit', True)
		self.open_file(data, **kwargs)
	def open_file(self, filename, **kwargs):
		self.connection = sqlite.connect(filename, **kwargs)
	def get_field_names_for_cursor(self, cur):
		return [ _[0] for _ in cur.description ]
	def get_table_defs(self):
		return list(self.generate_table("SELECT * FROM sqlite_master WHERE type='table';"))
	@property
	def table_names(self):
		return [_.name for _ in self.get_table_defs()]
###
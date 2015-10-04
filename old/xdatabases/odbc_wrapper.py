#!env python

from collections import namedtuple
from logging import debug, info, warning, error, critical

import pyodbc as odbc

from xdatabases import _xdatabase_base

class odbc_wrapper(_xdatabase_base):
	"""
	Abstract. Subclasses will need __init__ to probably run odbc.connect()
	"""
	
	pyodbc_TableDef = namedtuple('TableDef', 'table_cat table_schem table_name table_type remarks')
	# for some reason, pyodbc gives an extra field:
	pyodbc_ColumnDef = namedtuple('ColumnDef', 'table_cat table_schem table_name column_name data_type type_name column_size buffer_length decimal_digits num_prec_radix nullable remarks column_def sql_data_type sql_datetime_sub char_octet_length ordinal_position is_nullable field_19')
	pyodbc_CursorDescription = namedtuple('CursorDescription', 'name type_code display_size internal_size precision scale null_ok')
	
	def get_table_defs(self):
		with self.cursor() as cur:
			return [ self.pyodbc_TableDef(*t) for t in cur.tables(tableType='TABLE').fetchall() ]
	def get_field_defs_for_cursor(self, cur):
		return [ self.pyodbc_CursorDescription(*_) for _ in cur.description ]
	def get_field_names_for_cursor(self, cur):
		return [ _.name for _ in self.get_field_defs_for_cursor(cur) ]
	@property
	def table_names(self):
		return [_.table_name for _ in self.get_table_defs() ]

#!env python
from MDB import debug, info, warning, error, critical
from as_array import pyodbc_MDB_np

#import pandas as pd

def generate_date_dimension(*args, **kwargs):
	for _ in pd.date_range(*args, **kwargs):
		yield _, _.year, _.month, _.day, _.dayofweek
#
class pyodbc_MDB_pd(pyodbc_MDB_np):
	def create_date_dimension(self, *args, **kwargs):
		"""
		Assumes nocommit=False
		"""
		ID_name = kwargs.pop('ID', 'DateID')
		field_names = ['DateValue', 'Year',    'Month',   'Day',     'DayOfWeek']
		field_types = ['DATE',      'INTEGER', 'INTEGER', 'INTEGER', 'INTEGER']
		co = db.get_create_coroutine('DateDimensions', field_names, field_types, ID=ID_name)
		co.next()
		for _ in generate_date_dimension(*args, **kwargs):
			co.send(_)
if __name__ == '__main__':
	with pyodbc_MDB_pd('foo.mdb', nocommit=False) as db:
		db.create_date_dimension(start='2013-01-01', end='2013-06-26')
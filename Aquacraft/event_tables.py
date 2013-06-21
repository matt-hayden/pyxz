#!env python
from itertools import groupby

import numpy as np

from TraceWizard4.MDB_numpy import MDB_File

class AquacraftEventTable8(MDB_File):
	"""
	Expects a specific 8-field row:
		'Keycode', 'SumAs', 'CountAs', 'StartTime', 'Duration', 'Peak', 'Volume', 'Mode'
	Note: 'ModeFreq' is ignored
	
	Returns a specific numpy format:
		'Fixture', 'StartTime', 'Duration', 'Peak', 'Volume', 'Mode', 'FirstCycle'
	
	>>> fn  = r'Z:\Projects\IRWD SF Study 2005\T4 FT and DB\+All Sites_CalSF\Cal_SF_2011.mdb'
	>>> tn  = 'qunionCombinedAllEvents'
	>>> db  = AquacraftEventTable8(fn)
	>>> ets = db.generate_event_tables(tn)
	"""
	event_table_sql = 'select {1} from {0} where (SumAs is not NULL) order by Keycode, StartTime, Duration;'
	input_field_names = 'Keycode SumAs CountAs StartTime Duration Peak Volume Mode'.split()
	output_dtype = np.dtype([('Fixture',		('S', 15)),
							 ('StartTime',		'datetime64[s]'),
							 ('Duration',		np.float),
							 ('Peak',			np.float),
							 ('Volume',			np.float),
							 ('Mode',			np.float),
							 ('FirstCycle',		np.bool)])
	@staticmethod
	def standardize_fixture(SumAs, CountAs = ''):
		"""
		Returns:
			name		string
			first_cycle	bool	
		"""
		s, c = (SumAs or '').strip(), (CountAs or '').strip()
		fixture, first_cycle = '', False
		if not s:
			return fixture, first_cycle
		if s.endswith('@'):
			fixture = s.replace('@','').strip()
			first_cycle = True
		if s == c:
			first_cycle = True
		if fixture.startswith('Clothes'):
			fixture = 'Clothes washer'
		return fixture or s, first_cycle
	@staticmethod
	def row_factory(*row):
		Fixture, FirstCycle = AquacraftEventTable8.standardize_fixture(row[1], row[2])
		return (Fixture,)+row[3:]+(FirstCycle,)
#		Fixture, FirstCycle = AquacraftEventTable8.standardize_fixture(row.SumAs, row.CountAs)
#		return (Fixture, row.StartTime, row.Duration, row.Peak, row.Volume, row.Mode, FirstCycle)
	def generate_event_tables(self, *args, **kwargs):
		"""
		Input:	a table or sql statement with a very specific Aquacraft format
		Output:	a dict of {'Keycode':table, ...}
		"""
		tables = {}
		with self.execute(*args, **kwargs) as cursor:
			print cursor.fetchone()
			for keycode, rows in groupby(cursor, lambda _:_[0]):
				assert keycode not in tables
				fr = rows.next()
				print len(fr), fr
				tables[keycode] = np.fromiter((self.row_factory(*_) for _ in rows),
											  dtype=self.output_dtype)
		return tables
class AquacraftEventTable9(AquacraftEventTable8):
	"""
	Expects a specific 9-field row:
		'Keycode', 'SumAs', 'CountAs', 'StartTime', 'Duration', 'Peak', 'Volume', 'Mode', 'ModeFreq'
	Note: 'ModeFreq' was deleted in TraceWizard5, so this class is only useful
	for TraceWizard4-era event databases.
	
	Returns the same format as AquacraftEventTable8
	
	>>> fn  = r'Z:\Projects\IRWD SF Study 2005\T4 FT and DB\+All Sites_CalSF\Cal_SF_2011.mdb'
	>>> tn  = 'qunionCombinedAllEvents'
	>>> db  = AquacraftEventTable9(fn)
	>>> ets = db.generate_event_tables(tn)
	"""
	input_field_names = 'Keycode SumAs CountAs StartTime Duration Peak Volume Mode ModeFreq'.split()
	output_dtype = np.dtype([('Fixture',		('S', 15)),
							 ('StartTime',		'datetime64[s]'),
							 ('Duration',		np.float),
							 ('Peak',			np.float),
							 ('Volume',			np.float),
							 ('Mode',			np.float),
							 ('FirstCycle',		np.bool)])
class REUWS1999EventTable(AquacraftEventTable9):
	"""
	The event table from the original REUWS 1999 study has some unique problems:
	* Leaks are collected into a single daily leak event
	* StartTime and Duration are possibly missing
	* Event names use numerical and '@' suffixes differently
	"""
	def row_factory(*row):
		pass ### TODO
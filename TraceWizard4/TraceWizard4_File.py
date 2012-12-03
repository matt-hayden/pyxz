from collections import namedtuple
from datetime import timedelta
from itertools import groupby
from logging import debug, info, warning, error, critical

from MDB_File import MDB_File
from MeterMaster_Common import MeterMaster_Common, TraceWizard_Common, EventRow_midpoint

# identical to TW5 Parser:
Interval = namedtuple('Interval', 'min max')

class TraceWizard4_File_Error(Exception):
	pass
class TraceWizard4_File(TraceWizard_Common):
	format = "TraceWizard4" # default, could be tuned by detecting modifications to the file's template
	storage_interval = timedelta(seconds=10.0)
	#flow_multiplier = 10.0/60.0 # default, could be detected from flows table
	#
	#default_storage_interval = timedelta(seconds=10)
	flows_query = '''select EventID, StartTime as DateTimeStamp, Rate as RateData from Flows order by StartTime'''
	events_query = '''SELECT Events.ID, Fixtures.Name, Events.StartTime as DateTimeStamp, Events.Duration, Events.Peak, Events.Volume, Events.Mode, Events.ModeFreq FROM Fixtures RIGHT JOIN (Events INNER JOIN EventFixtures ON Events.ID = EventFixtures.IDEvent) ON Fixtures.ID = EventFixtures.IDFixture order by StartTime'''
	fixture_profiles_query = '''select * from Fixtures order by ID'''
	#
	default_file_extension = '.TWDB'
	#
	def __init__(self, data, load = True, **kwargs):
		self.filename = None
		if type(data) == str:
			if os.path.exists(data):
				if load:
					self.from_file(data)
				else:
					self.filename = data
			elif os.path.exists(os.path.split(data)[0]): # stub for write implementation
				self.filename = data
			elif load:
				self.from_query(data)
		#else:
		#	self.from_iterable(data)
	def from_file(self,
				  filename,
				  load_flows = True,
				  load_fixtures = True,
				  load_extras = ['Parameters', 'Meta'],
				  driver_name = None):
		self.filename = filename
		db = MDB_File(filename, driver_name)
		#
		self.flows = []
		if load_flows:
			self.flows = list(db.generate_query(self.flows_query))
			if len(self.flows) > 0:
				info("%d flow data points" % len(self.flows))
			else:
				error("No flow data points loaded")
		self.fixture_profiles = []
		if load_fixtures:
			self.fixture_profiles = list(db.generate_query(self.fixture_profiles_query))
			if len(self.fixture_profiles) > 0:
				info("%d fixture profiles" % len(self.flows))
			else:
				error("No fixture profiles")
		available_extra_tables = (set(load_extras) & set(db.table_names))
		debug("%d extra tables" % len(available_extra_tables))
		if available_extra_tables:
			self.extras = {}
			for table_name in available_extra_tables:
				info("Loading table [%s]" % table_name)
				self.extras[table_name] = list(db.generate_table(table_name))
		# events:
		self.events = list(db.generate_query(self.events_query))
		# maybe events_header should be set here
		if len(self.events) > 0:
			info("%d events" % len(self.events))
		else:
			critical("No events loaded")
		#
		# replacement for stuff found in other format's define_log_attributes:
		#
		try:
			fn = os.path.split(self.filename)[-1]
			n = os.path.splitext(fn)[0]
			if not n:
				# LogFileName found only in TW5
				fn = os.path.split(self.log_attributes['LogFileName'])[-1]
				n = "(from %s)" % fn
			self.label = n
		except:
			self.label = ''
	def print_summary(self):
		print "%d fixture profiles" % (len(self.fixture_profiles))
		print "%d events, %d flows between %s and %s" % (len(self.events), len(self.flows), self.begins, self.ends)
if __name__ == '__main__':
	import logging
	import os.path
	#
	logging.basicConfig(level=logging.DEBUG)
	#
	#desktop=os.path.expandvars('%UserProfile%\Desktop')
	tempdir=os.path.expandvars('%TEMP%\example-traces')
	fn = os.path.join(tempdir, '67096.TDB.MDB')
	print "Using", fn, "(%s)" % ("found" if os.path.exists(fn) else "not found")
	t = TraceWizard4_File(fn, driver_name = 'adodbapi')
	print t
	t.print_summary()
	for d, fs in t.get_flows_by_day():
		print d, sum([ f.RateData for f in fs ])*t.flow_multiplier
from collections import namedtuple
from datetime import timedelta
from itertools import groupby
from logging import debug, info, warning, error, critical
import os.path

import TraceWizard4
from MDB_File import MDB_File

class TraceWizard4_File_Error(Exception):
	pass
class TraceWizard4_File(TraceWizard4.TraceWizard_Common):
	format = "TDB"
	storage_interval = timedelta(seconds=10.0)
	volume_units = 'Gallons'
	#
	has_log_attribute_section = False
	has_flow_section = True
	#
	flows_query = '''select EventID, StartTime as DateTimeStamp, Rate as RateData from Flows order by Flows.ID'''
	events_query = '''SELECT Events.ID as EventID, Fixtures.Name, Events.StartTime as DateTimeStamp, Events.Duration, Events.Peak, Events.Volume, Events.Mode, Events.ModeFreq FROM Fixtures RIGHT JOIN (Events INNER JOIN EventFixtures ON Events.ID = EventFixtures.IDEvent) ON Fixtures.ID = EventFixtures.IDFixture order by Events.ID'''
	fixture_profiles_query = '''select * from Fixtures order by ID'''
	#
	def __init__(self, data, load = True, **kwargs):
		self.filename = None
		if type(data) == str:
			if os.path.exists(data):
				if load:
					self.from_file(data, **kwargs)
				else:
					self.filename = data
			elif os.path.exists(os.path.split(data)[0]): # stub for write implementation
				self.filename = data
			elif load:
				info("Unsure what to open, trying '%s' as a SQL query" % data)
				self.from_query(data, **kwargs)
		#else:
		#	self.from_iterable(data)
	#
	def get_total_volume(self,
						 ignored_classes=['Noise', 'Duplicate', 'Unclassified']):
		return sum(e.Volume for e in self.events if e.Name not in ignored_classes)
	#
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
			self.label = n
		except:
			self.label = ''
	def print_summary(self):
		print "%d fixture profiles" % (len(self.fixture_profiles))
		print "%f %s, %d events, %d flows between %s and %s" % (self.get_total_volume(), self.volume_units, len(self.events), len(self.flows), self.begins, self.ends)
if __name__ == '__main__':
	import logging
	#
	logging.basicConfig(level=logging.DEBUG)
	#
	#desktop=os.path.expandvars('%UserProfile%\Desktop')
	tempdir=os.path.expandvars('%TEMP%\example-traces')
	fn = os.path.join(tempdir, '67096.TDB')
	print "Using", fn, "(%s)" % ("found" if os.path.exists(fn) else "not found")
	t = TraceWizard4_File(fn) # , driver_name = 'adodbapi')
	print t
	t.print_summary()
	#for d, fs in t.get_flows_by_day():
	#	print d, sum([ f.RateData for f in fs ])*t.flow_multiplier
	total = t.get_total_volume()
	for e, fs in t.get_events_and_flows():
		print "Event:", e
		print "Flows:", fs
		break
	for e, rs in t.get_events_and_rates():
		print "Event:", e
		print "Rates:", rs
		break
from collections import namedtuple
from datetime import timedelta
from itertools import groupby, ifilter	
from logging import debug, info, warning, error, critical
import os.path

from _common import *
from MDB_File import MDB_File

class TraceWizard4_File_Error(Exception):
	pass
class TraceWizard4_File(TraceWizard_Common):
	@staticmethod
	def fixture_keyer(event):
		return event.Name
	@staticmethod
	def first_cycle_fixture_keyer(event):
		return (event.Name, "@" in event.Name)
	@staticmethod
	def Class_from_fixture_name(fixture_name):
		for i in [str(i) for i in range(1,9)]:
			if fixture_name.endswith(i):
				return fixture_name.replace(i,'').strip()
		return fixture_name
				
	# Defaults:
	default_event_fields = ['EventID', 'Name', 'DateTimeStamp', 'Duration', 'Peak', 'Volume', 'Mode', 'ModeFreq']
	ignored_classes=['Noise', 'Duplicate', 'Unclassified']
	volume_units = 'Gallons'
	#
	has_log_attribute_section = False
	has_flow_section = True
	#
	flows_query = '''select EventID, StartTime as DateTimeStamp, Rate as RateData from Flows order by Flows.ID'''
	events_query = '''SELECT Events.ID as EventID, Fixtures.Name, Events.StartTime as DateTimeStamp, Events.Duration, Events.Peak, Events.Volume, Events.Mode, Events.ModeFreq FROM Fixtures RIGHT JOIN (Events INNER JOIN EventFixtures ON Events.ID = EventFixtures.IDEvent) ON Fixtures.ID = EventFixtures.IDFixture order by Events.ID'''
	fixture_profiles_query = '''select * from Fixtures order by ID'''
	#
	def __init__(self, data, **kwargs):
		load = kwargs.pop('load', True)
		self.path = ''
		self.label = ''
		if type(data) == str:
			if os.path.exists(data):
				if load:
					self.from_file(data, **kwargs)
				else:
					self.path = data
			elif os.path.exists(os.path.dirname(data)): # stub for write implementation
				self.path = data
			elif load:
				info("Unsure what to open, trying '%s' as a SQL query" % data)
				self.from_query(data, **kwargs)
		#else:
		#	self.from_iterable(data)
		self.storage_interval = timedelta(seconds=10.0)
	#
	def get_logical_events(self):
		"""
		Chop off incomplete days at the beginning and ending of logging (based
		on flow data points, not events) and add a _count_ field to each event,
		signifying the number of events it counts as (currently between 0 and 
		1). Events are returned in the same order as the .events array.
		"""
		try:
			fields = [ d[0] for d in self.events[0].cursor_description]
		except: # not all drivers have cursor_description
			fields = self.default_event_fields
		TraceWizard4_Event = namedtuple('TraceWizard4_Event', fields+['Class', 'FirstCycle','count'])
		begin_ts, end_ts = self.get_complete_days(logical = True, typer = datetime)
		for row in self.events:
			if (begin_ts <= row.DateTimeStamp <= end_ts):
				n = row.Name.strip()
				if any(ifilter(n.upper().startswith, self.cyclers)):
					#e.count = 1 if n.endswith('@') else 0
					fc = n.endswith('@')
					c = 1 if e.FirstCycle else 0
					yield TraceWizard4_Event(*row, Class=self.Class_from_fixture_name(row.Name), FirstCycle=fc, count=c)
				else:
					#e.count = 1
					yield TraceWizard4_Event(*row, Class=self.Class_from_fixture_name(row.Name), FirstCycle=False, count=1)
	#
	def get_total_volume(self):
		return sum(e.Volume for e in self.events if e.Name not in self.ignored_classes)
	#
	def from_file(self, filename, **kwargs):
		load_flows = kwargs.pop('load_flows', True)
		load_fixtures = kwargs.pop('load_fixtures', True)
		load_extras = kwargs.pop('load_extras', ['Parameters', 'Meta'])
		driver_name = kwargs.pop('driver_name', None)
		#
		self.path = filename
		db = MDB_File(filename, driver_name)
		self.format = driver_name
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
				info("%d fixture profiles" % len(self.fixture_profiles))
			else:
				error("No fixture profiles")
		if db.table_names: # this is available only for some drivers
			available_extra_tables = (set(load_extras) & set(db.table_names))
			debug("%d extra tables" % len(available_extra_tables))
			if available_extra_tables:
				self.extras = {}
				for table_name in available_extra_tables:
					info("Loading table [%s]" % table_name)
					self.extras[table_name] = list(db.generate_table(table_name))
		else:
			self.extras = {}
			for table_name in load_extras:
				try:
					info("Loading table [%s]" % table_name)
					self.extras[table_name] = list(db.generate_table(table_name))
				except:
					debug("%s not found" % table_name)
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
			fn = os.path.basename(self.path)
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
	t = TraceWizard4_File(fn)
	print t
	t.print_summary()
	#for d, fs in t.get_flows_by_day():
	#	print d, sum([ f.RateData for f in fs ])*t.flow_multiplier
	total = t.get_total_volume()
	for e, fs in t.get_events_and_flows():
		if e.Class == 'Toilet':
			print "Event:", e
			print "Flows:", fs[0], "...", fs[-1]
			break
	for e, rs in t.get_events_and_rates():
		if e.Class == 'Toilet':
			print "Event:", e
			print "Rates:", rs[0], "...", rs[-1]
			break
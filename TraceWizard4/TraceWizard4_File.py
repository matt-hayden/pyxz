from collections import namedtuple
from datetime import timedelta
from itertools import groupby
from logging import debug, info, warning, error, critical

from MDB_File import MDB_File

# identical to TW5 Parser:
Interval = namedtuple('Interval', 'min max')

class TraceWizard4_File:
	default_storage_interval = timedelta(seconds=10)
	flows_query = '''select EventID, StartTime, Rate from Flow'''
	events_query = '''select ID as EventID, Name, StartTime, Duration, Peak, Volume, Mode, ModeFreq from [Event Summary]'''
	fixture_profiles_query = '''select * from EventFixtures'''
	#VirtualFixtures is ignored
	#
	default_file_extension = '.TWDB'
	#
	def from_file(self,
				  filename,
				  load_flows = True,
				  load_fixtures = True,
				  load_extras = ['Parameters', 'Meta'],
				  driver_name = None):
		db = MDB_File(filename, driver_name)
		self.events = list(db.generate_table(self.events_query))
		# maybe events_header should be set here
		if len(self.events) > 0:
			info("%d events" % len(self.events))
		else:
			critical("No events loaded")
		#
		if load_flows:
			self.flows = list(db.generate_table(self.flows_query))
			if len(self.flows) > 0:
				info("%d flow data points" % len(self.flows))
			else:
				error("No flow data points loaded")
		if load_fixtures:
			self.fixture_profiles = list(db.generate_table(self.fixture_profiles_query))
			if len(self.fixture_profiles) > 0:
				info("%d fixture profiles" % len(self.flows))
			else:
				error("No fixture profiles")
		if load_extras:
			self.extras = {}
			for table_name in (set(load_extras) & set(self.table_names)):
				self.extras[table_name] = list(db.generate_table(table_name))
				info("%s loaded" % table_name)
	@property
	def timespan(self):
		try:
			return Interval(self.flows[0].DateTimeStamp,
							self.flows[-1].DateTimeStamp+self.default_storage_interval)
		except Exception as e:
			error("Timespan error: %s" % e)
			return None
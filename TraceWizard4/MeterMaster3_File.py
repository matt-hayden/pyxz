from collections import namedtuple
from datetime import timedelta
from itertools import groupby
from logging import debug, info, warning, error, critical

from MDB_File import MDB_File

# identical to TW5 Parser:
Interval = namedtuple('Interval', 'min max')

seconds_fields = 'StorageInterval',
text_fields = 'City Make Note State PhoneNumber PostalCode Model CustomerName Unit Address CustomerID Size'.strip()
def format_log_attribute(key, value, float_t=float):
	if key in seconds_fields:
		try:
			td = timedelta(seconds=float(value))
		except:
			error("Interval %s not recognized",
				  value)
			td = value
		return key, td
	elif key in text_fields:
		return key, value.strip()
	# else:
	return key, value

class MeterMaster3_File:
	default_flow_multiplier = 10.0/60.0
	warning_flows_table_duration_tolerance = timedelta(hours=1)
	#
	def __init__(self, data):
		self.from_file(data)
	def from_file(self, filename, load_data = True, load_headers = True, driver_name = None):
		db = MDB_File(filename, driver_name)
		if load_data:
			self.flows = list(db.generate_table('MMData'))
			assert len(self.flows) > 0
		if load_headers:
			d = {}
			t = list(db.generate_table('Customer'))
			assert len(t) == 1
			d.update(t[0]._asdict())
			#
			t = list(db.generate_table('MeterInfo'))
			assert len(t) == 1
			d.update(t[0]._asdict())
			#
			self.define_log_attributes([(k,v) for k,v in d.iteritems()])
	#
	def define_log_attributes(self, pairs):
		if type(pairs) == dict:
			self.log_attributes = pairs
		else:
			self.log_attributes = dict([format_log_attribute(k,v) for k,v in pairs if k not in (None,'')])
		debug("%d datalogger attributes",
			  len(self.log_attributes))
		# Not very similar to MeterMaster4:
		storage_interval_delta = self.log_attributes['NumberOfIntervals']*self.log_attributes['StorageInterval']
		t = self.timespan
		if t:
			flows_table_duration = t[-1] - t[0]
			d = flows_table_duration - storage_interval_delta
			if abs(d) > self.warning_flows_table_duration_tolerance:
				warning("Difference of %s between MMData and NumberOfIntervals",
						d)
	@property
	def units(self):
		return self.log_attributes['Unit']
	@property
	def logged_volume(self):
		return self.log_attributes['MMVolume']
	@property
	def flow_multiplier(self):
		# identical to MM4
		try:
			m = self.log_attributes['StorageInterval'].seconds/60.0
			if m > 0:
				return m
		except:
			warning("Bad storage interval; defaulting to %s.",
					self.default_flow_multiplier)
		return self.default_flow_multiplier
	def get_flows_by_day(self):
		# identical to MM4	
		FlowDay = namedtuple('FlowDay', 'day flows')
		for d, f in groupby(self.flows, key=lambda f: f.DateTimeStamp.date()):
			yield FlowDay(d, tuple(f))
	@property
	def timespan(self):
		try:
			return Interval(self.flows[0].DateTimeStamp,
							self.flows[-1].DateTimeStamp+self.log_attributes['StorageInterval'])
		except:
			return None
	#
if __name__ == '__main__':
	import logging
	import os.path
	#
	logging.basicConfig(level=logging.DEBUG)
	#
	#desktop=os.path.expandvars('%UserProfile%\Desktop')
	tempdir=os.path.expandvars('%TEMP%\example-traces')
	fn = os.path.join(tempdir, '67096.MDB')
	m = MeterMaster3_File(fn)
	for d, fs in m.get_flows_by_day():
		print d, sum([ f.RateData for f in fs ])*m.flow_multiplier
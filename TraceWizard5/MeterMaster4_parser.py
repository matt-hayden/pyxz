from collections import namedtuple
import csv
from datetime import datetime, timedelta
from itertools import groupby
import os.path
from cStringIO import StringIO
import re

from CSV_with_header import CSV_with_header

version_regex = re.compile('[vV]?(?P<version_string>[\d.]*\d)')
# Attribute field stuff:
duration_regex = re.compile('(?P<days>\d+) days [+] (?P<hours>\d+):(?P<minutes>\d+)(:(?P<seconds>\d+))?')
duration_fields = 'TotalTime',
float_fields = 'BeginReading', 'ConvFactor', 'EndReading', 'MMVolume', 'RegVolume'
seconds_fields = 'StorageInterval',
int_fields = 'NumberOfIntervals',

def format_log_attribute(key, value, float_t=float):
	if key in float_fields:
		return key, float_t(value)
	if key in int_fields:
		return key, int(value)
	if key in seconds_fields:
		try:
			td = timedelta(seconds=float(value))
		except:
			td = value
		return key, td
	if key in duration_fields:
		m = duration_regex.match(value)
		if m:
			try:
				td = timedelta(days=int(m.group('days')),
							   hours=int(m.group('hours')),
							   minutes=int(m.group('minutes')),
							   seconds=int(m.group('seconds') or 0)
							   )
			except:
				td = value
			return key, td
	# else:
	return key, value
#
class MeterMaster4_CSV(CSV_with_header):
	data_table_name = 'flows'
	end_of_header = 'DateTimeStamp,RateData\n'	# EOL needed here
	#
	default_flow_multiplier = 10.0/60.0
	flows_header = ['DateTimeStamp', 'RateData']
	flow_timestamp_format = '%m/%d/%Y %I:%M:%S %p'
	ratedata_t = float
	#
	def _build_FlowRow(self):
		self.FlowRow = namedtuple('FlowRow', self.flows_header)
	#
	def parse_flow_line(self, line):
		return self.FlowRow(
			datetime.strptime(line[0], self.flow_timestamp_format),
			self.ratedata_t(line[1])
			)
	def parse_CSV(self, iterable = None):
		iterable = iterable or open(self.filename)
		#
		line_number = self.header_lines = self.parse_CSV_header(iterable)
		self.define_log_attributes(self.header)
		#
		self._build_FlowRow()
		self.__dict__[self.data_table_name] = [ self.parse_flow_line(l) for l in csv.reader(iterable) ]
	#
	def define_log_attributes(self, pairs):
		"""
		Extended checks on the MeterMaster attributes, taking a list of
		2-tuples.
		"""
		self.log_attributes = dict([format_log_attribute(k,v) for k,v in pairs if k not in (None,'')])
		#
		try:
			vs = self.log_attributes['MM100 Data Export']
			self.format = 'MM100 Data Export'
			try:
				m = version_regex.match(vs)
				self.version = tuple(m.group('version_string').split('.'))
			except:
				self.version = vs
		except:
			self.version = None
		#
		#storage_interval_delta = timedelta(seconds = self.log_attributes['NumberOfIntervals']*self.log_attributes['StorageInterval'])
		storage_interval_delta = seconds = self.log_attributes['NumberOfIntervals']*self.log_attributes['StorageInterval']
		assert storage_interval_delta == self.log_attributes['TotalTime']
	#
	@property
	def flow_multiplier(self):
		try:
			m = self.log_attributes['StorageInterval'].seconds/60.0
			if m > 0:
				return m
		except:
			print "Error"
		return self.default_flow_multiplier
	@property
	def units(self):
		return self.log_attributes['Unit']
	@property
	def logged_volume(self):
		return sum(f.RateData for f in self.flows)*self.flow_multiplier
	def get_flows_by_day(self):
		FlowDay = namedtuple('FlowDay', 'day flows')
		for d, f in groupby(self.flows, key=lambda f: f.DateTimeStamp.date()):
			yield FlowDay(d, tuple(f))
	#
	def print_summary(self):
		print "Volume by day:"
		for d, fa in self.get_flows_by_day():
			daily_total = sum(f.RateData for f in fa)*self.flow_multiplier
			print d, " = ", daily_total, self.units
#
if __name__ == '__main__':
	import os.path
	#desktop=os.path.expandvars('%UserProfile%\Desktop')
	tempdir=os.path.expandvars('%TEMP%\example-traces')
	fn = os.path.join(tempdir, '12S704.csv')
	print fn, "found:", os.path.exists(fn)
	m = MeterMaster4_CSV(fn)
	m.print_summary()
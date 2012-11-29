from collections import namedtuple
import csv
from datetime import datetime, timedelta
from itertools import groupby
from logging import debug, info, warning, error, critical
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
			error("Interval %s not recognized",
				  value)
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
				error("Duration %s not recognized",
					  value)
				td = value
			return key, td
	# else:
	return key, value
#
class MeterMaster4_CSV(CSV_with_header):
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
	def parse_CSV_header(self, iterable = None):
		CSV_with_header.parse_CSV_header(self, iterable)
		self.define_log_attributes(self.header)
	def parse_CSV(self, iterable = None):
		if iterable is None:
			info("Reading CSV format from '%s'",
				 self.filename)
			iterable = open(self.filename)
		#
		line_number = self.parse_CSV_header(iterable)
		#
		self._build_FlowRow()
		self.flows = [ self.parse_flow_line(l) for l in csv.reader(iterable) ]
	#
	def define_log_attributes(self, pairs):
		"""
		Extended checks on the MeterMaster attributes, taking a list of
		2-tuples.
		"""
		if type(pairs) == dict:
			self.log_attributes = pairs
		else:
			self.log_attributes = dict([format_log_attribute(k,v) for k,v in pairs if k not in (None,'')])
		debug("%d datalogger attributes",
			  len(self.log_attributes))
		# Try to set the Brainard version:
		try:
			vs = self.log_attributes['MM100 Data Export']
			self.format = 'MM100 Data Export'
			try:
				m = version_regex.match(vs)
				self.version = tuple(m.group('version_string').split('.'))
				info("Opening %s file version %s",
					 self.format, self.version)
			except:
				error("Version string '%s' not recognized",
					  vs)
				self.version = vs
		except:
			warning("No '%s' version string",
					'MM100 Data Export')
			self.version = None
		#
		# These checks are similar to TraceWizard5:
		storage_interval_delta = self.log_attributes['NumberOfIntervals']*self.log_attributes['StorageInterval']
		d = self.log_attributes['TotalTime'] - storage_interval_delta
		if d:
			warning("Difference of %s between TotalTime and NumberOfIntervals",
					d)
	#
	@property
	def flow_multiplier(self):
		try:
			m = self.log_attributes['StorageInterval'].seconds/60.0
			if m > 0:
				return m
		except:
			warning("Bad storage interval; defaulting to %s.",
					self.default_flow_multiplier)
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
		print "Logging attributes:", self.log_attributes
		print "Volume by day:"
		for d, fa in self.get_flows_by_day():
			daily_total = sum(f.RateData for f in fa)*self.flow_multiplier
			print d, " = ", daily_total, self.units
#
if __name__ == '__main__':
	import logging
	import os.path
	#
	logging.basicConfig(level=logging.DEBUG)
	#
	#desktop=os.path.expandvars('%UserProfile%\Desktop')
	tempdir=os.path.expandvars('%TEMP%\example-traces')
	fn = os.path.join(tempdir, '12S704.csv')
	print fn, "found:", os.path.exists(fn)
	m = MeterMaster4_CSV(fn, load=False)
	m.parse_CSV_header()
	m.print_summary()
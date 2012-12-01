from collections import namedtuple
import csv
from datetime import datetime, timedelta
from logging import debug, info, warning, error, critical
import os.path
from cStringIO import StringIO
import re

from TraceWizard4.MeterMaster_Common import MeterMaster_Common
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
class MeterMaster4_CSV(CSV_with_header, MeterMaster_Common):
	end_of_header = 'DateTimeStamp,RateData\n'	# EOL needed here
	#
	#default_flow_multiplier = 10.0/60.0
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
		self.format = 'MM100 Data Export'
		self.version = None
		try:
			self.version = self.log_attributes[self.format]
			info("Opening %s file version %s",
				 self.format, self.version)
			try:
				m = version_regex.match(self.version)
				if m:
					self.version_tuple = tuple(m.group('version_string').split('.'))
			except:
				error("Version string '%s' not recognized",
					  self.version)
		except:
			warning("No '%s' version string",
					'MM100 Data Export')
		#
		# These checks are similar to TraceWizard5:
		storage_interval_delta = self.log_attributes['NumberOfIntervals']*self.log_attributes['StorageInterval']
		d = self.log_attributes['TotalTime'] - storage_interval_delta
		if d:
			warning("Difference of %s between TotalTime and NumberOfIntervals",
					d)
	def print_summary(self):
		print "Logging attributes:", self.log_attributes
		print "Volume by day:"
		for d, fa in self.get_flows_by_day():
			daily_total = sum(f.RateData for f in fa)*self.flow_multiplier
			print d, " = ", daily_total, self.volume_units
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
	m = MeterMaster4_CSV(fn, load=True)
	m.parse_CSV_header()
	m.print_summary()
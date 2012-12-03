from collections import namedtuple
import csv
from datetime import datetime, timedelta
from logging import debug, info, warning, error, critical
import os.path
from cStringIO import StringIO
import re

from TraceWizard4.MeterMaster_Common import MeterMaster_Common, ratedata_t, volume_t
from CSV_with_header import CSV_with_header

version_regex = re.compile('[vV]?(?P<version_string>[\d.]*\d)')
# Attribute field stuff:
duration_regex = re.compile('((?P<days>\d+) days)?[ +]*((?P<hours>\d+):(?P<minutes>\d+)(:(?P<seconds>\d+))?)?')
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
				td = timedelta(days=int(m.group('days') or 0),
							   hours=int(m.group('hours') or 0),
							   minutes=int(m.group('minutes') or 0),
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
	format = 'MM100 Data Export'
	#
	def parse_CSV_header(self, iterable = None):
		CSV_with_header.parse_CSV_header(self, iterable)
		#super(MeterMaster4_CSV, self).parse_CSV_header(iterable) # ?
		self.define_log_attributes(self.header)
	def parse_CSV(self,
				  iterable = None,
				  line_parser = None
				  ):
		if not line_parser:
			row_factory = namedtuple('FlowRow', self.flows_header)
			def line_parser(line):
				return row_factory(
					datetime.strptime(line[0], self.flow_timestamp_format),
					ratedata_t(line[1])
					)
		if iterable is None:
			info("Reading CSV format from '%s'",
				 self.filename)
			iterable = open(self.filename)
		#
		line_number = self.parse_CSV_header(iterable)
		#
		#self._build_FlowRow()
		#self.flows = [ line_parser(l) for l in csv.reader(iterable) ]
		self.flows = []
		for l in csv.reader(iterable):
			try:
				self.flows.append(line_parser(l))
			except Exception as e:
				debug("error parsing array '%s'" % l)
				raise e
	#
	def _check_log_attributes(self, format = 'MM100 Data Export'):
		# Try to set the Brainard version:
		self.format = format
		try:
			self.version = self.log_attributes[format]
			info("Opening %s file version %s" %(self.format, self.version))
			try:
				m = version_regex.match(self.version)
				if m:
					self.version_tuple = tuple(m.group('version_string').split('.'))
					del self.log_attributes[format]
			except:
				error("Version string '%s' not recognized",
					  self.version)
		except:
			warning("No '%s' version string" % format)
			self.version = None
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

	print "m =", m
	m.print_summary()
	print "Volume by day:"
	total = m.logged_volume
	for d, fs in m.get_flows_by_day():
		daily_total = sum([ f.RateData for f in fs ])*m.flow_multiplier
		print d, daily_total, m.volume_units, "(%5.1f%%)" % (100*daily_total/total)
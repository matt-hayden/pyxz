from collections import namedtuple
import csv
from datetime import datetime, timedelta
from logging import debug, info, warning, error, critical
import os.path
from cStringIO import StringIO
import re

import TraceWizard4
from CSV_with_header import CSV_with_header_and_version

def format_MeterMaster4_header(pairs):
	duration_regex = re.compile('((?P<days>\d+) days)?[ +]*((?P<hours>\d+):(?P<minutes>\d+)(:(?P<seconds>\d+))?)?')
	volume_t = TraceWizard4.volume_t
	#
	if type(pairs) == dict:
		row = pairs
	else:
		row = dict(pairs)
	if not row:
		return None
	d = {}
	d['CustomerID'] = row['CustomerID'].strip()
	d['CustomerName'] = row['CustomerName'].strip()
	d['Address'] = row['Address'].strip()
	d['City'] = row['City'].strip()
	d['State'] = row['State'].strip()
	d['PostalCode'] = row['PostalCode'].strip()
	d['PhoneNumber'] = row['PhoneNumber'].strip()
	d['Note'] = row['Note'].strip()
	# empty line in header would be here
	d['Make'] = row['Make'].strip()
	d['Model'] = row['Model'].strip()
	d['Size'] = row['Size'].strip()
	d['Unit'] = row['Unit'].strip()
	d['StorageInterval'] = timedelta(seconds=float(row['StorageInterval']))
	d['NumberOfIntervals'] = int(row['NumberOfIntervals'])
	m = duration_regex.match(row['TotalTime'])
	if m:
		d['TotalTime'] = timedelta(days=int(m.group('days') or 0),
								   hours=int(m.group('hours') or 0),
								   minutes=int(m.group('minutes') or 0),
								   seconds=int(m.group('seconds') or 0)
								   )
	else:
		d['TotalTime'] = row.TotalTime
	d['BeginReading'] = volume_t(row['BeginReading'])
	d['EndReading'] = volume_t(row['EndReading'])
	d['RegVolume'] = volume_t(row['RegVolume'])
	d['MMVolume'] = volume_t(row['MMVolume'])
	d['ConvFactor'] = float(row['ConvFactor'])
	return d

class MeterMaster4_CSV(TraceWizard4.MeterMaster_Common, CSV_with_header_and_version):
	end_of_header = 'DateTimeStamp,RateData\n'	# EOL needed here
	format = 'MM100 Data Export'	# key to the version tuple (beginning of CSV)
	#
	has_log_attribute_section = True
	has_flow_section = True
	#
	flows_header = ['DateTimeStamp', 'RateData']
	flow_timestamp_format = '%m/%d/%Y %I:%M:%S %p'
	#
	def __init__(self, *args, **kwargs):
		self.label = ''
		CSV_with_header_and_version.__init__(self, *args, **kwargs) # yuck
	#
	def define_log_attributes(self, pairs):
		self.log_attributes = format_MeterMaster4_header(pairs)
		#
		self.storage_interval = self.log_attributes['StorageInterval']
		#
		n = self.log_attributes['CustomerID']
		if not n:
			try:
				fn = os.path.split(self.path)[-1]
				n = os.path.splitext(fn)[0]
			except:
				n = "<%s>" % self.__class__.__name__
		self.label = n
	def parse_CSV(self,
				  iterable = None,
				  data_table_name = 'flows',
				  line_parser = None
				  ):
		if not line_parser:
			ratedata_t = TraceWizard4.ratedata_t
			row_factory = namedtuple('FlowRow', self.flows_header)
			def line_parser(line):
				return row_factory(
					datetime.strptime(line[0], self.flow_timestamp_format),
					ratedata_t(line[1])
					)
		if iterable is None:
			info("Reading CSV format from '%s'" % self.path)
			iterable = open(self.path)
		#
		line_number = self.parse_CSV_header(iterable)
		f = []
		for l in csv.reader(iterable):
			try:
				f.append(line_parser(l))
			except Exception as e:
				debug("error parsing array '%s'" % l)
				raise e
		self.__dict__[data_table_name] = f
		self._check_log_attributes()
	def parse_CSV_header(self, *args, **kwargs):
		line_number = CSV_with_header_and_version.parse_CSV_header(self, *args, **kwargs) # yuck
		self.define_log_attributes(self.header)
		return line_number
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
	m = MeterMaster4_CSV(fn) # , load=True)
	#m.parse_CSV_header()

	print "m =", m
	m.print_summary()
	print "Volume by day:"
	total = m.logged_volume
	for d, fs in m.get_flows_by_day():
		daily_total = sum([ f.RateData for f in fs ])*m.flow_multiplier
		print d, daily_total, m.volume_units, "(%5.1f%%)" % (100*daily_total/total)
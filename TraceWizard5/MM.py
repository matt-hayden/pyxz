from collections import namedtuple
import csv
from datetime import datetime, timedelta
from logging import debug, info, warning, error, critical
import os.path
from cStringIO import StringIO
import re

import TraceWizard4
from CSV_with_header import CSV_with_header_and_version

duration_regex = re.compile('((?P<days>\d+) days)?[ +]*((?P<hours>\d+):(?P<minutes>\d+)(:(?P<seconds>\d+))?)?')

def format_MeterMaster4_header(pairs, **kwargs):
	"""
	Takes an iterable or dictionary of attribute pairs, for example:
		[ ('CustomerID', '123'), ('RegVolume', '12,345.67'), ... ]
	These are assumed to be strings as provided by a (naive) CSV reader. 
	
	An optional volumetric parser, header_volume_t_formatter, can be used to 
	implement Decimal readings (instead of float) if preferred. This function
	must deal with some bugs in the MM100 program.
	"""
	debug("format_MeterMaster4_header")
	header_volume_t_formatter = kwargs.pop('header_volume_t_formatter', None)
	if not header_volume_t_formatter:
		def header_volume_t_formatter(text, volume_t = TraceWizard4.volume_t):
			return volume_t(text.replace(',',''))
	#
	if type(pairs) == dict:
		row = pairs
	else:
		row = dict(pairs)
	if not row:
		return None
	d = {}
	d['CustomerID']		= row['CustomerID'].strip()
	d['CustomerName']	= row['CustomerName'].strip()
	d['Address']		= row['Address'].strip()
	d['City']			= row['City'].strip()
	d['State']			= row['State'].strip()
	d['PostalCode']		= row['PostalCode'].strip()
	d['PhoneNumber']	= row['PhoneNumber'].strip()
	d['Note']			= row['Note'].strip()
	# empty line in header would be here
	d['Make']	= row['Make'].strip()
	d['Model']	= row['Model'].strip()
	d['Size']	= row['Size'].strip()
	d['Unit']	= row['Unit'].strip()
	try:
		d['StorageInterval'] = timedelta(seconds=float(row['StorageInterval']))
	except:
		warning("Bad storage interval string '{}'".format(row['StorageInterval'].strip()))
		d['StorageInterval'] = row['StorageInterval'].strip()
	try:
		d['NumberOfIntervals'] = int(row['NumberOfIntervals'])
	except:
		warning("Bad number of intervals string '{}'".format(row['NumberOfIntervals'].strip()))
		d['NumberOfIntervals'] = row['NumberOfIntervals'].strip()
	m = duration_regex.match(row['TotalTime'])
	if m:
		d['TotalTime'] = timedelta(days=int(m.group('days') or 0),
								   hours=int(m.group('hours') or 0),
								   minutes=int(m.group('minutes') or 0),
								   seconds=int(m.group('seconds') or 0)
								   )
	else:
#		d['TotalTime'] = row.TotalTime
		warning("Bad total time string '{}'".format(row['TotalTime'].strip()))
		d['TotalTime'] = row['TotalTime'].strip()
	for key in 'BeginReading EndReading RegVolume MMVolume'.split():
		try:
			d[key] = header_volume_t_formatter(row[key])
		except:
			warning("Bad {} string '{}'".format(key, row[key].strip()))
			d[key] = row[key].strip()
#	d['BeginReading'] = header_volume_t_formatter(row['BeginReading'])
#	d['EndReading'] = header_volume_t_formatter(row['EndReading'])
#	d['RegVolume'] = header_volume_t_formatter(row['RegVolume'])
#	d['MMVolume'] = header_volume_t_formatter(row['MMVolume'])
	try:
		"""
		Another MM100 bug? Commas instead of decimal points.
		"""
		d['ConvFactor'] = float(row['ConvFactor'].replace(",","."))
	except:
		warning("Bad conversion factor '{}'".format(row['ConvFactor'].strip()))
		d['ConvFactor'] = row['ConvFactor'].strip()
	return d

class MeterMaster4_CSV(TraceWizard4.MeterMaster_Common, CSV_with_header_and_version):
	data_table_name = 'flows'
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
		debug("MeterMaster4_CSV.__init__({})".format(','.join(args)))
		self.label = ''
		CSV_with_header_and_version.__init__(self, *args, **kwargs) # yuck
	#
	def define_log_attributes(self, pairs, **kwargs):
		debug("MeterMaster4_CSV.define_log_attributes")
		self.log_attributes = format_MeterMaster4_header(pairs, **kwargs)
		#
		self.storage_interval = self.log_attributes['StorageInterval']
		#
		n = self.log_attributes['CustomerID']
		old = self.label
		#
		if not n:
			try:
				dirname, basename = os.path.split(self.path)
				filepart, ext = os.path.splitext(basename)
				n = filepart
			except Exception as e:
				info("Filename '{}' somehow invalid: {}".format(self.path, e))
				n = "<%s>" % self.__class__.__name__
		if old.upper() != n.upper():
			debug("Label changed from '{}' to '{}'".format(old, n))
		self.label = n
	def parse_CSV(self, iterable = None, **kwargs):
		debug("MeterMaster4_CSV.parse_CSV")
		line_parser = kwargs.pop('line_parser', None)
		load_flows = kwargs.pop('load_flows', True)
		if not line_parser:
			ratedata_t = TraceWizard4.ratedata_t
			row_factory = namedtuple('FlowRow', self.flows_header)
			def line_parser(line):
				return row_factory(
					datetime.strptime(line[0], self.flow_timestamp_format),
					ratedata_t(line[1])
					)
		if not iterable:
			info("Reading CSV format from file '{}'".format(self.path))
			iterable = open(self.path)
		#
		line_number = self.parse_CSV_header(iterable, **kwargs)
		if load_flows:
			f = []
			for l in csv.reader(iterable):
				try:
					f.append(line_parser(l))
				except Exception as e:
					debug("error parsing array '%s'" % l)
					raise e
			self.__dict__[self.data_table_name] = f
			self._check_log_attributes()
	def parse_CSV_header(self, *args, **kwargs):
		debug("MeterMaster4_CSV.parse_CSV_header")
		line_number = CSV_with_header_and_version.parse_CSV_header(self, *args, **kwargs) # yuck
		"""
		Since the header is coming in tabular form, we collapse it down to two
		fields. This fixes a weird feature in MM100 where extra commas are 
		inserted because number formats are thousands-separated by commas.
		"""
		for el in self.header:
			if len(el) > 2:
				el[1] = ''.join(el[1:])
				del el[2:]
		self.define_log_attributes(self.header, **kwargs)
		return line_number
#
if __name__ == '__main__':
	import logging
	import sys
	#
	logging.basicConfig(level=logging.DEBUG)
	#
	#desktop=os.path.expandvars('%UserProfile%\Desktop')
	tempdir=os.path.expandvars('%TEMP%')
#	fn = os.path.join(tempdir, '12S704.csv')
	for arg in sys.argv[1:]:
		print arg, "found:", os.path.exists(arg)
		m = MeterMaster4_CSV(arg) # , load=True)
		#m.parse_CSV_header()

		print "m =", m
		print "Volume by day:"
		total = m.logged_volume
		for d, fs in m.get_flows_by_day():
			daily_total = sum([ f.RateData for f in fs ])*m.flow_multiplier
			print d, daily_total, m.volume_units, "(%5.1f%%)" % (100*daily_total/total)
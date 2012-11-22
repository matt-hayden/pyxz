from collections import namedtuple
import csv
from datetime import datetime, timedelta
import os.path
from cStringIO import StringIO
import re

from CSV_with_header import CSV_with_header

# Attribute field stuff:
duration_regex = re.compile('(?P<days>\d+) days [+] (?P<hours>\d+):(?P<minutes>\d+)(:(?P<seconds>\d+))?')
duration_fields = 'TotalTime',
float_fields = 'BeginReading', 'ConvFactor', 'EndReading', 'MMVolume', 'RegVolume', 'StorageInterval'
int_fields = 'NumberOfIntervals',

dequote_regex=re.compile('\\s*(["\'])(.*)\\1\\s*')

def dequote(text):
	m = dequote_regex.match(text)
	return m.groups()[-1] if m else text
def format_log_attribute(key, value, float_t=float):
	if key in float_fields:
		return key, float_t(value)
	if key in int_fields:
		return key, int(value)
#	if key in log_attribute_timestamp_fields:
#		try:
#			return key, datetime.strptime(value, log_attribute_timestamp_format)
#		except:
#			return format_log_attribute(key, dequote(value))
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
# Datapoint stuff:

#Unused?
#timestamp_regex = re.compile('[0-1]?\d/\d{1,2}/\d{2,4} [0-2]\d:\d{2}(:\d{2}) (am|AM|pm|PM)?')


#
class MeterMaster4_CSV(CSV_with_header):
	data_table_name = 'flows'
	end_of_header = 'DateTimeStamp,RateData\n'
	#
	flows_header = ['DateTimeStamp', 'RateData']
	ratedata_t = float
	timestamp_format = '%m/%d/%Y %I:%M:%S %p'
	#
	def _build_FlowRow(self):
		self.FlowRow = namedtuple('FlowRow', self.flows_header)
	#
	@property
	def log_attributes(self):
		return self.attributes
	def parse_flow_line(self, line, float_t=float):
		return self.FlowRow(
			datetime.strptime(line[0], self.timestamp_format),
			float_t(line[1])
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
		storage_interval_delta = timedelta(seconds = self.log_attributes['NumberOfIntervals']*self.log_attributes['StorageInterval'])
		assert storage_interval_delta == self.log_attributes['TotalTime']
	#
#
if __name__ == '__main__':
	import os.path
	#desktop=os.path.expandvars('%UserProfile%\Desktop')
	tempdir=os.path.expandvars('%TEMP%\example-traces')
	fn = os.path.join(tempdir, '12S704.csv')
	print fn, "found:", os.path.exists(fn)
	m = MeterMaster4_CSV(fn)
	
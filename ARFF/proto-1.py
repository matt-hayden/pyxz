#! env python
from collections import deque
import csv
from datetime import datetime, timedelta
from itertools import groupby
import re
from cStringIO import StringIO

"""
Read several versions of TraceWizard5 files. Should be refactored into several
files for clarity.
"""

dequote_regex=re.compile('\\s*(["\'])(.*)\\1\\s*')

log_attribute_timestamp_format = '%Y-%m-%d %H:%M:%S'
log_attribute_duration_regex = re.compile('(?P<days>\d+) days [+] (?P<hours>\d+):(?P<minutes>\d+)(:(?P<seconds>\d+))?')
log_attribute_duration_fields = 'TotalTime',
log_attribute_float_fields = 'BeginReading', 'ConvFactor', 'EndReading', 'MMVolume', 'RegVolume', 'StorageInterval'
log_attribute_int_fields = 'NumberOfIntervals',
log_attribute_timestamp_fields = 'LogEndTime', 'LogStartTime'
def dequote(text):
	m = dequote_regex.match(text)
	return m.groups()[-1] if m else text
def format_log_attribute(key, value, float_t=float):
	if key in log_attribute_float_fields:
		return key, float_t(value)
	if key in log_attribute_int_fields:
		return key, int(value)
	if key in log_attribute_timestamp_fields:
		try:
			return key, datetime.strptime(value, log_attribute_timestamp_format)
		except:
			return format_log_attribute(key, dequote(value))
	if key in log_attribute_duration_fields:
		m = log_attribute_duration_regex.match(value)
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

class dummy_storage1:
	def __init__(self):
		self.events = []
		self.flows = []
	def append_event(self, data):
		if data.strip():
			self.events.append(data)
	def append_flow(self, data):
		if data.strip():
			self.flows.append(data)
class dummy_storage2(dummy_storage1):
	def __init__(self):
		#dummy_storage1.__init__(self)
		self.log_attributes = {}
	def append_log_attribute(self,key,value):
		self.log_attributes[key] = value # mysterious error here

class ARFF_format:
	comment_regex=re.compile('%\s*(?P<comment>.*)')
	#
	relation_section_regex=re.compile('@RELATION\s+(?P<relation_name>.*)')
	relation_regex=re.compile('@ATTRIBUTE\s+(?P<attribute_name>\w+)\s+(?P<attribute_parameters>.*)')
class ARFF_header(ARFF_format):
	### ARFF statements:
	header_format_regex=re.compile('%\s*Format:\s*(?P<header_format>.*)')
	header_version_regex=re.compile('%\s?Version:\s*(?P<header_version>.*)')
	data_section_regex=re.compile('@DATA')
	@staticmethod
	def header_version_parser(match):
		try:
			version_tuple = tuple([ int(d) for d in match.group('header_version').split('.') ])
			return version_tuple
		except:
			return None
	@staticmethod
	def sniff_version(parseme, max_lines = 30, start_line = 0):
		"""
		Returns a tuple like ('File format', Format version(), Number of header lines)
		"""
		#line_number=0
		next_section=ARFF_header.relation_section_regex.match
		for line_number, line in enumerate(parseme, start=start_line+1):
			if line_number > max_lines:
				return None, None, line_number
			n=next_section(line)
			if n:
				break
			# else:
			m = ARFF_header.header_format_regex.match(line)
			if m:
				format = m.group('header_format')
				continue
			m = ARFF_header.header_version_regex.match(line)
			if m:
				version = ARFF_header.header_version_parser(m)
				continue
			m = ARFF_header.comment_regex.match(line)
			if m and m.group('comment'):
				print line_number, line
		return format, version, line_number
#
class TraceWizard5_parser(ARFF_header, dummy_storage1):
	### Custom comment statements not standard in ARFF
	event_timestamp_format = log_attribute_timestamp_format # '%Y-%m-%d %H:%M:%S'
	#
	fixture_profile_section_regex=re.compile('% @FIXTURE PROFILES')
	fixture_profile_header_regex=re.compile('% FixtureClass,MinVolume,MaxVolume,MinPeak,MaxPeak,MinDuration,MaxDuration,MinMode,MaxMode')
	# right now, each fixture profile is simply a comment
	log_attribute_section_regex=re.compile('% @LOG')
	log_attribute_regex=re.compile('%\s+(?P<attribute_name>\w+)\s*[,]\s*(?P<attribute_value>.*)')
	# right now, each logged attribute is simply a comment
	has_flow_section=True
	flow_section_regex=re.compile('% @FLOW')
	flow_timestamp_format = event_timestamp_format
	#
	def __init__(self, data = None):
		self._build_parse_sectioner()
		if data:
			if type(data) == str:
				self.from_file(data)
			else:
				self.from_iterable(data)
	#
	def _build_parse_sectioner(self):
		"""
		List of custom comment section break designators that come AFTER the
		ARFF relations. Make sure this hard-coded list jives with the parsing
		logic.
		"""
		#ps = []
		ps = deque()
		if self.has_fixture_profile_section:
			ps.append(self.fixture_profile_section_regex.match)
		if self.has_log_attribute_section:
			ps.append(self.log_attribute_section_regex.match)
		ps.append(self.data_section_regex.match)
		if self.has_flow_section:
			ps.append(self.flow_section_regex.match)
		ps.reverse() # Hmm
		self._parse_sectioner = ps
	#
	def print_summary(self):
		print "<", self.__class__, ">", self.format, "format, version", self.version
		print "Attributes:"
		for n, l in enumerate(self.attributes):
			print '\t', n, l
		if self.has_fixture_profile_section:
			print "Fixture profiles:"
			for n, l in enumerate(self.fixture_profiles):
				print '\t', n, l
		if self.has_log_attribute_section:
			print "Logging attributes:", self.log_attributes
		print len(self.events), "events"
		print self.events[0], " - ", self.events[-1]
		if self.has_flow_section:
			print len(self.flows), "data points"
			print self.flows[0], " - ", self.flows[-1]
	#
	TraceWizard4_events_header = ['eventid',
								  'class',
								  'starttime',
								  'endtime',
								  'duration',
								  'volume',
								  'peak',
								  'mode'
								  ]
	@property
	def events_header(self):
		return [a[0] for a in self.attributes]
	flows_header = 'eventid', 'starttime', 'duration', 'rate'
	flows_units = self.log_attributes['Unit']+"/minute"
	def parse_flow_line(self, line, float_t=float):
		return (int(line[0]),
				datetime.strptime(line[1], self.flow_timestamp_format),
				float_t(line[2]),
				float_t(line[3])
				)
	def get_TraceWizard4_events(self, 
								first_cycle_classes=['Clotheswasher', 'Dishwasher', 'Shower'],
								first_cycler=lambda s: s+"@"):
		fields = [ self.events_header.index(s) for s in self.TraceWizard4_events_header ]
		first_cycle_index = self.events_header.index('firstcycle')
		i_name_index = self.events_header.index('class')
		o_name_index = self.TraceWizard4_events_header.index('class')
		for e in self.events:
			name = e[i_name_index]
			row = [e[i] for i in fields]
			if e[first_cycle_index] and first_cycler and (name in first_cycle_classes):
				name=first_cycler(name)
				row[o_name_index] = name
			yield row
	def get_events_and_flows(self, field_name = 'eventid'):
		"""
		Returns an iterable of the following structure:
			[ event, [flow_0, ..., flow_n]]
		To discern the fields in event or flows, use the flows_header and 
		events_header members.
		"""
		assert self.has_flow_section
		key_field = self.flows_header.index(field_name)
		for k, g in groupby(self.flows, lambda e: e[key_field]):
			yield (self.events[k],list(g))
	def get_events_and_rates(self, flow_field_name = 'rate'):
		"""
		Returns an iterable of the following structure:
			[ event, [rate_0, ..., rate_n]]
		To discern the fields in event, use events_header. The units of flow
		rate are available in the flows_units member.
		"""
		rate_field = self.flows_header.index(flow_field_name)
		for e, g in self.get_events_and_flows():
			yield (e, tuple([f[rate_field] for f in g]) )
	#
	def parse_header(self, parseme):
		"""
		Read the TraceWizard5-specific header after sniffing the version.
		"""
		self.format, self.version, line_number = self.sniff_version(parseme)
		# Relation attributes (mandatory)
		next_section=self._parse_sectioner.pop()
		a = []
		for line_number, line in enumerate(parseme, start=line_number+1):
			n=next_section(line)
			if n:
				break
			# else:
			m = self.relation_regex.match(line) # TODO
			if m:
				a.append( (m.group('attribute_name'), m.group('attribute_parameters')) )
		self.attributes = a
		# Fixture list (optional)
		self.fixture_profiles = []
		if self.has_fixture_profile_section:
			next_section=self._parse_sectioner.pop()
			fp = []
			for line_number, line in enumerate(parseme, start=line_number+1):
				n=next_section(line)
				if n:
					break
				# else:
				m = self.comment_regex.match(line)
				if m:
					fp.append(m.group('comment'))
			self.fixture_profiles = fp
		# Datalogger attributes (optional)
		self.log_attributes = {}
		if self.has_log_attribute_section:
			next_section=self._parse_sectioner.pop()
			la = []
			for line_number, line in enumerate(parseme, start=line_number+1):
				n=next_section(line)
				if n:
					break
				# else:
				m = self.log_attribute_regex.match(line)
				if m:
					la.append((m.group('attribute_name'), m.group('attribute_value')))
			self.define_log_attributes(la)
		return line_number
	#
	def define_log_attributes(self, attributes):
		"""
		Extended checks on the MeterMaster attributes, taking a list of
		2-tuples.
		"""
		self.log_attributes = dict([format_log_attribute(k,v) for k,v in attributes])
		timestamp_delta = self.log_attributes['LogEndTime'] - self.log_attributes['LogStartTime']
		storage_interval_delta = timedelta(seconds = self.log_attributes['NumberOfIntervals']*self.log_attributes['StorageInterval'])
		assert timestamp_delta == storage_interval_delta
	#
	def parse_TraceWizard5_ARFF(self, iterable):
		"""
		Parsing an input file beyond sniffing the version and reading the
		header.
		"""
		line_number = self.parse_header(iterable)
		# Data points (mandatory)
		sio=StringIO()
		if len(self._parse_sectioner): # there's a comment section following
			next_section=self._parse_sectioner.pop()
			for line_number, line in enumerate(iterable, start=line_number+1):
				n = next_section(line)
				if n:
					break
				# else:
				if line.strip():
					sio.write(line)
		else:
			next_section = None
			for line_number, line in enumerate(iterable, start=line_number+1):
				sio.write(line)
		print "Events parsing produced", sio.tell(), "characters"
		sio.seek(0)
		self.events = [ self.parse_event_line(l) for l in csv.reader(sio) ]
		sio.close()
		# Flows
		self.flows = []
		if self.has_flow_section:
			sio=StringIO()
			next_section = None
			for line_number, line in enumerate(iterable, start=line_number+1):
				m = self.comment_regex.match(line) # TODO
				if m:
					sio.write(m.group('comment'))
					sio.write('\n')
			sio.seek(0)
			self.flows = [ self.parse_flow_line(l) for l in csv.reader(sio) ]
			sio.close()
	def from_file(self, filename):
		with open(filename) as fi:
			self.from_iterable(fi)
	def from_iterable(self, iterable):
		self.parse_TraceWizard5_ARFF(iterable)
class TraceWizard5100_parser(TraceWizard5_parser):
	minimum_version = (5,1,0,0)
	number_of_event_fields = 12
	has_fixture_profile_section=False
	has_log_attribute_section=False
	#
	def parse_event_line(self, line, float_t=float):
		return (int(line[0]),
				datetime.strptime(line[1], self.event_timestamp_format),
				datetime.strptime(line[2], self.event_timestamp_format),
				float_t(line[3]),
				bool(line[4]),
				bool(line[5]),
				line[6],
				float_t(line[7]),
				float_t(line[8]),
				float_t(line[9]),
				line[10].strip(),
				line[11]
				)
				
class TraceWizard51021_parser(TraceWizard5100_parser):
	minimum_version = (5,1,0,21)
	has_fixture_profile_section=True
class TraceWizard51030_parser(TraceWizard51021_parser):
	minimum_version = (5,1,0,30)
	has_log_attribute_section=True
TraceWizard5_classes = [ TraceWizard51030_parser, TraceWizard51021_parser, TraceWizard5100_parser ]
def TraceWizard5_File(filename, parent=TraceWizard5_parser):
	"""
	Convenience function to return the correct parser for an ARFF file.
	"""
	with open(filename) as fi:
		format, version, line_number = parent.sniff_version(fi)
		t = None
		for vclass in TraceWizard5_classes:
			if version >= vclass.minimum_version:
				break
	return vclass(filename)
if __name__ == '__main__':
	import os.path
	#desktop=os.path.expandvars('%UserProfile%\Desktop')
	tempdir=os.path.expandvars('%TEMP%\example-traces')
	example_traces = ['01_07nov2011_16nov2011.twdb',
					  '09_22oct2011_append_21dec2011.twdb',
					  '12S704.twdb'
					  ]
	fn = os.path.join(tempdir, example_traces[-1])
	t = TraceWizard5_File(fn)
	#t4 = list(t.get_TraceWizard4_events())
	fbe = list(t.get_events_and_rates())
	t.print_summary()
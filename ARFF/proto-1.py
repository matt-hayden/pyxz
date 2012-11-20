#! env python
from datetime import datetime
import re

"""
Read several versions of TraceWizard5 files.
"""


log_attribute_timestamp_format = '%Y-%m-%d %H:%M:%S'
log_attribute_duration_format = '%d days + %H:%M:%S'
log_attribute_float_fields = 'BeginReading', 'ConvFactor', 'EndReading', 'MMVolume', 'RegVolume', 'StorageInterval'
log_attribute_int_fields = 'NumberOfIntervals',
log_attribute_timestamp_formats = 'LogEndTime', 'LogStartTime'
def dequote(text):
	if text.startswith('"') and text.endswith('"'):
		return text[1:-1]
def format_log_attribute(key, value):
	if key in log_attribute_float_fields:
		return key, float(value)
	if key in log_attribute_int_fields:
		return key, int(value)
	if key in log_attribute_timestamp_formats:
		try:
			return key, datetime.strptime(value, log_attribute_timestamp_format)
		except:
			return format_log_attribute(key, dequote(value))
	else:
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
	comment_regex=re.compile('%(?P<comment>.*)')
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
	#has_fixture_profile_section=True
	fixture_profile_section_regex=re.compile('% @FIXTURE PROFILES')
	fixture_profile_header_regex=re.compile('% FixtureClass,MinVolume,MaxVolume,MinPeak,MaxPeak,MinDuration,MaxDuration,MinMode,MaxMode')
	# right now, each fixture profile is simply a comment
	#has_log_attribute_section=True
	log_attribute_section_regex=re.compile('% @LOG')
	log_attribute_regex=re.compile('%\s+(?P<attribute_name>\w+)\s*[,]\s*(?P<attribute_value>.*)')
	# right now, each logged attribute is simply a comment
	has_flow_section=True
	flow_section_regex=re.compile('% @FLOW')
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
		ps = []
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
	def parse_header(self, parseme):
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
		#			self.append_log_attribute(m.group('attribute_name'),
		#									  m.group('attribute_value'))
		#			la[m.group('attribute_name')] = m.group('attribute_value')
					la.append(format_log_attribute(m.group('attribute_name'), m.group('attribute_value')))
			print la
			self.log_attributes = dict(la)
		return line_number
	#
	def parse_TraceWizard5_ARFF(self, parseme):
		line_number = self.parse_header(parseme)
		# Data points (mandatory)
		self.events=[]
		if len(self._parse_sectioner): # there's a comment section following
			next_section=self._parse_sectioner.pop()
			for line_number, line in enumerate(parseme, start=line_number+1):
				n = next_section(line)
				if n:
					break
				# else:
				#self.events.append(line)
				self.append_event(line)
		else:
			next_section = None
			for line_number, line in enumerate(parseme, start=line_number+1):
				#self.events.append(line)
				self.append_event(line)
		# Flows
		self.flows = []
		if self.has_flow_section:
			next_section = None
			for line_number, line in enumerate(parseme, start=line_number+1):
				#line_number += 1
				m = self.comment_regex.match(line) # TODO
				if m:
					#self.flows.append(line)
					self.append_flow(line)
	def from_file(self, filename):
		with open(filename) as fi:
			self.from_iterable(fi)
	def from_iterable(self, iterable):
		self.parse_TraceWizard5_ARFF(iterable)
class TraceWizard5100_parser(TraceWizard5_parser):
	minimum_version = (5,1,0,0)
	has_fixture_profile_section=False
	has_log_attribute_section=False
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
	desktop=os.path.expandvars('%UserProfile%\Desktop')
	for fn in ['01_07nov2011_16nov2011.twdb',
			   '09_22oct2011_append_21dec2011.twdb',
			   '12S704.twdb'
			   ]:
		fn = os.path.join(desktop, 'example-traces', fn)
		t = TraceWizard5_File(fn)
		t.print_summary()
from collections import deque, namedtuple
from contextlib import closing
import csv
from datetime import datetime, timedelta
from itertools import groupby
from logging import debug, info, warning, error, critical
import os.path
import re
from cStringIO import StringIO

from ARFF_format import ARFF_format_with_version, ARFF_format_Error, dequote
import MeterMaster4_parser
import TraceWizard4

def format_TraceWizard5_header(pairs):
	log_attribute_timestamp_format = '%Y-%m-%d %H:%M:%S' # different from MeterMaster4_parser
	def timeconvert(s):
		try:
			return datetime.strptime(s, log_attribute_timestamp_format)
		except ValueError:
			return timeconvert(dequote(s))
	debug("%d log attributes in file" % len(pairs))
	#for n, (k, v) in enumerate(pairs):
	#	print n, k, v
	di = dict(pairs)
	do = MeterMaster4_parser.format_MeterMaster4_header(pairs)
	do['LogStartTime'] = timeconvert(di['LogStartTime'])
	do['LogEndTime'] = timeconvert(di['LogEndTime'])
	do['LogFileName'] = di['LogFileName'].strip()
	#
	do['Code'] = di['Code']
	do['Nutation'] = di['Nutation']
	do['LED'] = di['LED']
	do['TotalPulses'] = di['TotalPulses']
	do['ConvFactorType'] = di['ConvFactorType']
	do['DatabaseMultiplier'] = di['DatabaseMultiplier']
	do['CombinedFile'] = di['CombinedFile']
	do['DoublePulse'] = di['DoublePulse']
	debug("%d log attributes read" % len(do))
	return do
#
respell = {
	'eventid':		'EventID',
	'starttime':	'StartTime',
	'endtime':		'EndTime',
	'firstcycle':	'FirstCycle',
	'class':		'Class',
	'classifiedusingfixturelist':	'ClassifiedUsingFixtureList',
	'manuallyapproved':				'ManuallyApproved',
	'manuallyclassifiedfirstcycle':	'ManuallyClassifiedFirstCycle'
	}
#
class TraceWizard5_parser_Error(ARFF_format_Error):
	pass
class TraceWizard5_parser(ARFF_format_with_version, TraceWizard4.TraceWizard_Common):
	event_timestamp_format = '%Y-%m-%d %H:%M:%S'
	format = ''
	has_flow_section=True
	#
	@staticmethod
	def fixture_keyer(event):
		return event.Class
	@staticmethod
	def first_cycle_fixture_keyer(event):
		return (event.Class, event.FirstCycle)
	@staticmethod
	def attribute_name_formatter(s):
		"""
		Called by a method in ARFF_format_with_version
		"""
		if s in respell:
			return respell[s]
		else:
			return s.title()
	#
	fixture_profile_section_regex=re.compile('% @FIXTURE PROFILES')
	fixture_profile_header_regex=re.compile('% FixtureClass,MinVolume,MaxVolume,MinPeak,MaxPeak,MinDuration,MaxDuration,MinMode,MaxMode')
	# right now, each fixture profile is simply a comment
	log_attribute_section_regex=re.compile('% @LOG')
	log_attribute_regex=re.compile('%\s+(?P<attribute_name>\w+)\s*[,]\s*(?P<attribute_value>.*)')
	# right now, each logged attribute is simply a comment
	flow_section_regex=re.compile('% @FLOW')
	flow_timestamp_format = event_timestamp_format
	#
	def __init__(self, data = None, **kwargs):
		load = kwargs.pop('load', True)
		self.path = ''
		self.label = ''
		self._build_parse_sectioner()
		if type(data) == str:
			if os.path.exists(data):
				if load:
					self.from_file(data, **kwargs)
				else:
					self.path = data
			elif os.path.exists(os.path.split(data)[0]): # stub for write implementation
				self.path = data
			#elif load:
			#		self.from_iterable(data)
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
	@property
	def events_header(self):
		return [a.Name for a in self.attributes]
	#
	flows_header = 'EventID', 'DateTimeStamp', 'Duration', 'RateData'
	#
	def get_TraceWizard4_events(self, 
								first_cycle_classes=['Clotheswasher', 'Dishwasher', 'Shower'],
								first_cycler=lambda s: s+"@",
								row_factory = None):
		"EventID Class StartTime EndTime Duration Volume Peak Mode"
		if not row_factory:
			row_factory = namedtuple('TraceWizard4_EventRow',
				"EventID Class StartTime EndTime Duration Volume Peak Mode"
				)
		for e in self.events:
			myClass = e.Class
			if e.FirstCycle and (myClass in first_cycle_classes) and first_cycler:
				myClass = first_cycler(myClass)
			yield row_factory(
					e.EventID,
					myClass,
					e.StartTime,
					e.EndTime,
					e.Duration,
					e.Volume,
					e.Peak,
					e.Mode
				)
	#
	def parse_ARFF_header(self, iterable = None, **kwargs):
		"""
		Read the TraceWizard5-specific header after sniffing the version.
		"""
		load_fixture_profiles = kwargs.pop('load_fixture_profiles', True)
		load_log_attributes = kwargs.pop('load_log_attributes', True)
		#
		if iterable is None:
			info("Reading ARFF header from '%s'",
				 self.path)
			iterable = open(self.path)
		self.format, self.version, line_number = self.sniff_version(iterable)
		info("Opening %s file version %s" % (self.format, self.version))
		# Relation attributes (mandatory)
		line_number = self.define_attributes(iterable,
											 line_number = line_number,
											 next_section = self._parse_sectioner.pop()
											 )
		debug("%d ARFF attributes" % len(self.attributes))
		# Fixture list (optional)
		self.fixture_profiles = []
		if self.has_fixture_profile_section:
			next_section=self._parse_sectioner.pop()
			if load_fixture_profiles:
				expected_header_row = "% {}".format(','.join(self.fixture_profile_header))
				fixture_line_parser = self.parse_fixture_profile_line
				#
				fp = []
				if self.check_fixture_profile_header:
					n = iterable.next()
					header_row = n.strip()
					if header_row == expected_header_row:
						debug("Flows header:" + header_row)
					else:
						error("Unexpected fixture profile header '%s'" + header_row)
						iterable.insert(0, n)
				#
				for line_number, line in enumerate(iterable, start=line_number+1):
					n=next_section(line)
					if n:
						break
					# else:
					if line.strip():
						m = self.comment_regex.match(line)
						if m:
							fp.append(fixture_line_parser(m.group('comment')))
						else:
							error("Fixture profile row '%s' not recognized" % line)
				self.fixture_profiles = fp
				debug("%d fixture profiles" % len(self.fixture_profiles))
		# Datalogger attributes (optional)
		self.log_attributes = {}
		if self.has_log_attribute_section:
			next_section=self._parse_sectioner.pop()
			if load_log_attributes:
				la = []
				for line_number, line in enumerate(iterable, start=line_number+1):
					n=next_section(line)
					if n:
						break
					# else:
					if line.strip():
						m = self.log_attribute_regex.match(line)
						if m:
							la.append((m.group('attribute_name'), m.group('attribute_value')))
						else:
							error("Datalogger attribute row '%s' not recognized",
								  line)
				self.define_log_attributes(la)
				self._check_log_attributes()
		else:
			info("No datalogger attributes")
		self.has_header = True
		return line_number
	#
	def define_log_attributes(self, pairs):
		"""
		Should be subclassed for versions with different capabilites
		"""
		self.log_attributes = format_TraceWizard5_header(pairs)
		#
		self.storage_interval = self.log_attributes['StorageInterval']
		#
	#
	def get_original_MeterMaster4(self, make_relative = True):
		log_filename = self.log_attributes['LogFileName']
		if not os.path.exists(log_filename):
			error("'%s' no longer exists")
			return None
		#
		mm_log_filename = log_filename
		if make_relative:
			c = os.path.commonprefix([self.path, log_filename])
			if c:
				mm_log_filename = log_filename.replace(c, "", count=1)
		return MeterMaster4_parser.MeterMaster4_CSV(mm_log_filename)
	#
	def parse_ARFF(self, iterable = None, **kwargs):
		"""
		Parsing an input file beyond sniffing the version and reading the
		header.
		"""
		flow_line_parser = kwargs.pop('flow_line_parser', None)
		load_flows = kwargs.pop('load_flows', True)
		#
		line_number = self.parse_ARFF_header(iterable, **kwargs)
		line_number = self.parse_ARFF_body(iterable,
										   line_number=line_number,
										   member_name=self.event_table_name,
										   next_section=self._parse_sectioner.pop(),
										   **kwargs)
		debug("%d events" % len(self.events))
		# Flows
		self.flows = []
		if self.has_flow_section:
			next_section = None
			if load_flows:
				if not flow_line_parser:
					ratedata_t = TraceWizard4.ratedata_t
					row_factory = namedtuple('FlowRow', self.flows_header)
					def flow_line_parser(row):
						return row_factory(
							int(row[0]),
							datetime.strptime(row[1], self.flow_timestamp_format),
							timedelta(seconds=float(row[2])),
							ratedata_t(row[3])
							)
				with closing(StringIO()) as sio:
					for line_number, line in enumerate(iterable, start=line_number+1):
						m = self.comment_regex.match(line)
						if m:
							#assert not m.group('comment').startswith("%")
							sio.write(m.group('comment'))
							sio.write('\n')
					debug("Flows parsing produced %d characters" % sio.tell())
					sio.seek(0)
					#
					for l in csv.reader(sio):
						try:
							self.flows.append(flow_line_parser(l))
						except Exception as e:
							debug("Error parsing array '%s': %s" % (l, e))
							#raise e
					#sio.close()
				debug("%d flows" % len(self.flows))
	#
	def get_total_volume(self,
						 ignored_classes=['Noise', 'Duplicate', 'Unclassified']):
		return sum(e.Volume for e in self.events if e.Class not in ignored_classes)
	#
	def print_summary(self):
		print "%d attributes, %d fixture profiles, %d log attributes" % (len(self.attributes), len(self.fixture_profiles), len(self.log_attributes))
		print "%f %s, %d events, %d flows between %s and %s" % (self.get_total_volume(), self.volume_units, len(self.events), len(self.flows), self.begins, self.ends)
#
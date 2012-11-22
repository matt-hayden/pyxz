from collections import deque, namedtuple
from contextlib import closing
import csv
from datetime import datetime, timedelta
from itertools import groupby
import os.path
import re
from cStringIO import StringIO

from ARFF_header import ARFF_header
import MeterMaster4_parser

log_attribute_timestamp_format = '%Y-%m-%d %H:%M:%S' # different from MeterMaster4_parser
log_attribute_timestamp_fields = 'LogEndTime', 'LogStartTime'
dequote_regex=re.compile('\\s*(["\'])(.*)\\1\\s*')

def dequote(text):
	m = dequote_regex.match(text)
	return m.groups()[-1] if m else text
def format_log_attribute(key, value):
	"""
	Wrapper around the identical function in MeterMaster4_parser. There are a
	few added fields.
	"""
	if key in log_attribute_timestamp_fields:
		try:
			return key, datetime.strptime(value, log_attribute_timestamp_format)
		except:
			return format_log_attribute(key, dequote(value))
	# else:
	return MeterMaster4_parser.format_log_attribute(key, value)
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
TraceWizard4_EventRow = namedtuple('TraceWizard4_EventRow',
	"EventID Class StartTime EndTime Duration Volume Peak Mode"
	)
#
class TraceWizard5_parser(ARFF_header):
	### Custom comment statements not standard in ARFF
	event_timestamp_format = log_attribute_timestamp_format
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
	def __init__(self, data = None, load = True):
		self.filename = None
		self._build_parse_sectioner()
		if data:
			if type(data) == str:
				if os.path.exists(data):
					if load:
						self.from_file(data)
				elif os.path.exists(os.path.split(data)[0]): # stub for write implementation
					self.filename = data
				else:
					if load:
						self.from_iterable(data)
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
	def _build_EventRow(self):
		"""
		Events are reported as namedtuple objects. This means you can refer to
		row.starttime rather than row[3], row[4], or row[5] if that field moves
		places between formats.
		"""
		self.EventRow = namedtuple('EventRow', self.events_header)
	def _build_FlowRow(self):
		self.FlowRow = namedtuple('FlowRow', self.flows_header)
	#
	@property
	def events_header(self):
		return [a[0] for a in self.attributes]
	events_units = 'Gallons'
	#
	flows_header = 'EventID', 'DateTimeStamp', 'Duration', 'RateData'
	@property
	def flows_units(self):
		return self.log_attributes['Unit']+"/minute"
	#
	def parse_flow_line(self, line, ratedata_t=float, row_factory = None):
		row_factory = row_factory or self.FlowRow
		return row_factory(
			int(line[0]),
			datetime.strptime(line[1], self.flow_timestamp_format),
			timedelta(seconds=float(line[2])),
			ratedata_t(line[3])
			)
	def get_TraceWizard4_events(self, 
								first_cycle_classes=['Clotheswasher', 'Dishwasher', 'Shower'],
								first_cycler=lambda s: s+"@",
								row_factory = None):
		"EventID Class StartTime EndTime Duration Volume Peak Mode"
		#
		row_factory = row_factory or TraceWizard4_EventRow
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
	def get_events_and_flows(self):
		"""
		Returns an iterable of the following structure:
			[ event, [flow_0, ..., flow_n]]
		To discern the fields in event or flows, use the flows_header and 
		events_header members.
		"""
		EventFlows = namedtuple('EventFlows', 'event flows')
		assert self.has_flow_section
		for k, g in groupby(self.flows, lambda e: e.EventID):
			yield EventFlows(self.events[k],tuple(g))
	def get_events_and_rates(self):
		"""
		Returns an iterable of the following structure:
			[ event, [rate_0, ..., rate_n]]
		To discern the fields in event, use events_header. The units of flow
		rate are available in the flows_units member.
		"""
		for e, g in self.get_events_and_flows():
			yield (e, tuple([f.RateData for f in g]) )
	@staticmethod
	def EventRow_midpoint(e):
		return e.StartTime+e.Duration/2
	def get_events_by_day(self, day_decider=None):
		"""
		Returns all events broken into 24-hour periods. Events spanning
		midnight are, by default, not broken across days. Flows for events
		spanning midnight are all assigned to a single day, the same day as
		that event. Returns:
			[ date, [event_0, [flow_00, ..., flow_0j]], ...,
					[event_n, [flow_n0, ..., flow_nk]] ]
		"""
		if not day_decider:
			def day_decider(t):
				return self.EventRow_midpoint(t[0]).date()
		for k, ef in groupby(self.get_events_and_flows(), key=day_decider):
			yield (k, tuple(ef))
	#
	def parse_ARFF_header(self,
					 iterable = None,
					 forbidden_attribute_names = ['class']
					 ):
		"""
		Read the TraceWizard5-specific header after sniffing the version.
		"""
		iterable = iterable or open(self.filename)
		self.format, self.version, line_number = self.sniff_version(iterable)
		# Relation attributes (mandatory)
		next_section=self._parse_sectioner.pop()
		a = []
		for line_number, line in enumerate(iterable, start=line_number+1):
			n=next_section(line)
			if n:
				break
			# else:
			m = self.relation_regex.match(line)
			if m:
				name = m.group('attribute_name')
				if name in respell:
					name = respell[name]
				else:
					name = name.title()
				a.append( (name, m.group('attribute_parameters')) )
		self.attributes = a
		### EventRow is built at the earliest possible time
		self._build_EventRow()
		# Fixture list (optional)
		self.fixture_profiles = []
		if self.has_fixture_profile_section:
			next_section=self._parse_sectioner.pop()
			fp = []
			for line_number, line in enumerate(iterable, start=line_number+1):
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
			for line_number, line in enumerate(iterable, start=line_number+1):
				n=next_section(line)
				if n:
					break
				# else:
				m = self.log_attribute_regex.match(line)
				if m:
					la.append((m.group('attribute_name'), m.group('attribute_value')))
			self.define_log_attributes(la)
		self.has_header = True
		return line_number
	#
	def define_log_attributes(self, pairs):
		"""
		Extended checks on the MeterMaster attributes, taking a list of
		2-tuples.
		"""
		self.log_attributes = dict([format_log_attribute(k,v) for k,v in pairs if k not in (None,'')])
		#
		timestamp_delta = self.log_attributes['LogEndTime'] - self.log_attributes['LogStartTime']
		storage_interval_delta = timedelta(seconds = self.log_attributes['NumberOfIntervals']*self.log_attributes['StorageInterval'])
		assert timestamp_delta == storage_interval_delta
		#
		log_filename = self.log_attributes['LogFileName']
		if log_filename:
			original_log_exists = os.path.exists(log_filename)
			if original_log_exists:
				c = os.path.commonprefix([t.filename, self.log_attributes['LogFileName'] ])
				if c:
					relative_log_file = self.log_attributes['LogFileName'].replace(c, "")
				else:
					relative_log_file = log_filename
				print "Original log file", relative_log_file, "exists"
	#
	def parse_ARFF(self,
				   iterable = None):
		"""
		Parsing an input file beyond sniffing the version and reading the
		header.
		"""
		iterable = iterable or open(self.filename)
		line_number = self.parse_ARFF_header(iterable)
		# Data points (mandatory)
		with closing(StringIO()) as sio:
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
			#sio.close()
		# Flows
		self.flows = []
		if self.has_flow_section:
			###
			self._build_FlowRow()
			###
			with closing(StringIO()) as sio:
				next_section = None
				for line_number, line in enumerate(iterable, start=line_number+1):
					m = self.comment_regex.match(line) # TODO
					if m:
						sio.write(m.group('comment'))
						sio.write('\n')
				sio.seek(0)
				self.flows = [ self.parse_flow_line(l) for l in csv.reader(sio) ]
				#sio.close()
	def from_file(self, filename):
		with open(filename) as fi:
			self.from_iterable(fi)
		self.filename = filename
	def from_iterable(self, iterable):
		self.parse_ARFF(iterable)
		self.filename = None
	#
	@property
	def logged_volume(self):
		return self.get_total_volume(ignored_classes=None)
	def get_total_volume(self, ignored_classes=['Noise', 'Duplicate', 'Unclassified']):
		return sum(e.Volume for e in self.events if e.Class not in ignored_classes)
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
		print "Volume by day:"
		for d, ef in self.get_events_by_day():
			daily_total = sum(e.Volume for (e, f) in ef)
			print d, " = ", daily_total, self.events_units
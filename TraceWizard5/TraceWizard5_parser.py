from collections import deque, namedtuple
from contextlib import closing
import csv
from datetime import datetime, timedelta
from itertools import groupby
from logging import debug, info, warning, error, critical
import os.path
import re
from cStringIO import StringIO

from ARFF_format import ARFF_format_with_version, dequote
import MeterMaster4_parser

log_attribute_timestamp_format = '%Y-%m-%d %H:%M:%S' # different from MeterMaster4_parser
log_attribute_timestamp_fields = 'LogEndTime', 'LogStartTime'
#
# Should be in TraceWizard common
def EventRow_midpoint(e):
	return e.StartTime+e.Duration/2
#
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
class TraceWizard5_parser(ARFF_format_with_version):
	# Custom comment statements are otherwise ignored in ARFF
	event_timestamp_format = log_attribute_timestamp_format
	event_table_name = 'events'
	#
	@staticmethod
	def attribute_name_formatter(s):
		"""
		Called in ARFF_format_with_version
		"""
		if s in respell:
			return respell[s]
		else:
			return s.title()
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
	ratedata_t=float
	#
	class TraceWizard5_parser_error(Exception):
		pass
	def __init__(self, data = None, load = True, **kwargs):
		self.filename = None
		self._build_parse_sectioner()
		if data:
			if type(data) == str:
				if os.path.exists(data):
					if load:
						self.from_file(data)
					else:
						self.filename = data
				elif os.path.exists(os.path.split(data)[0]):	# stub for write implementation
					self.filename = data
				else:
					if load:
						self.from_iterable(data)
			else:
				self.from_iterable(data)
	# maybe this goes into the common class:
	def __repr__(self):
		s = " ".join((self.__class__.__name__,
					  "(format '%s')" % self.format if self.format else '',
					  self.label))
		return "<%s>" % s.strip()
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
	@property
	def events_header(self):
		return [a.Name for a in self.attributes]
	events_units = 'Gallons'
	#
	@property
	def flows_units(self):
		return self.log_attributes['Unit']+"/minute"
	#
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
				return EventRow_midpoint(t[0]).date()
		for k, ef in groupby(self.get_events_and_flows(), key=day_decider):
			yield (k, tuple(ef))
	#
	def parse_ARFF_header(self, iterable = None):
		"""
		Read the TraceWizard5-specific header after sniffing the version.
		"""
		#
		if iterable is None:
			info("Reading ARFF header from '%s'",
				 self.filename)
			iterable = open(self.filename)
		self.format, self.version, line_number = self.sniff_version(iterable)
		info("Opening %s file version %s",
			 self.format, self.version)
		# Relation attributes (mandatory)
		line_number = self.define_attributes(iterable,
											 line_number = line_number,
											 next_section = self._parse_sectioner.pop()
											 )
		debug("%d ARFF attributes",
			  len(self.attributes))
		# Fixture list (optional)
		self.fixture_profiles = []
		if self.has_fixture_profile_section:
			expected_header_row = "% {}".format(','.join(self.fixture_profile_header))
			fixture_line_parser = self.parse_fixture_profile_line # TODO
			#
			next_section=self._parse_sectioner.pop()
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
						error("Fixture profile row '%s' not recognized",
							  line)
			self.fixture_profiles = fp
			debug("%d fixture profiles",
				  len(self.fixture_profiles))
		else:
			info("No fixture profiles")
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
				if line.strip():
					m = self.log_attribute_regex.match(line)
					if m:
						la.append((m.group('attribute_name'), m.group('attribute_value')))
					else:
						error("Datalogger attribute row '%s' not recognized",
							  line)
			self.define_log_attributes(la)
		else:
			info("No datalogger attributes")
		self.has_header = True
		return line_number
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
		#
		# These checks are similar to MeterMaster4:
		storage_interval_delta = self.log_attributes['NumberOfIntervals']*self.log_attributes['StorageInterval']
		d = self.log_attributes['TotalTime'] - storage_interval_delta
		if d:
			warning("Difference of %s between TotalTime and NumberOfIntervals" % d)
		# also check against LogStartTime and LogEndTime, which are not in MeterMaster4_CSV:
		timestamp_delta = self.log_attributes['LogEndTime'] - self.log_attributes['LogStartTime']
		d = timestamp_delta - storage_interval_delta
		if d:
			warning("Difference of %s between LogEndTime and NumberOfIntervals" % d)
		#
		n = self.log_attributes['CustomerID']
		if not n:
			try:
				fn = os.path.split(self.filename)[-1]
				n = os.path.splitext(fn)[0]
				if not n:
					fn = os.path.split(self.log_attributes['LogFileName'])[-1]
					n = "(from %s)" % fn
			except:
				n = "<%s>" % self.__class__.__name__
		self.label = n
	def get_original_MeterMaster4(self, make_relative = True):
		log_filename = self.log_attributes['LogFileName']
		if not os.path.exists(log_filename):
			error("'%s' no longer exists")
			return None
		#
		mm_log_filename = log_filename
		if make_relative:
			c = os.path.commonprefix([self.filename, log_filename])
			if c:
				mm_log_filename = log_filename.replace(c, "", count=1)
		return MeterMaster4_parser.MeterMaster4_CSV(mm_log_filename)
	#
	def parse_ARFF(self, 
				   iterable = None, 
				   line_parser = None, 
				   flow_line_parser = None):
		"""
		Parsing an input file beyond sniffing the version and reading the
		header.
		"""
		line_number = self.parse_ARFF_header(iterable)
		line_number = self.parse_ARFF_body(iterable,
										   line_number=line_number,
										   member_name=self.event_table_name,
										   next_section=self._parse_sectioner.pop()
										   )
		debug("%d events" % len(self.events))
		# Flows
		self.flows = []
		if self.has_flow_section:
			next_section = None
			if not flow_line_parser:
				row_factory = namedtuple('FlowRow', self.flows_header)
				def flow_line_parser(row):
					return row_factory(
						int(row[0]),
						datetime.strptime(row[1], self.flow_timestamp_format),
						timedelta(seconds=float(row[2])),
						self.ratedata_t(row[3])
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
		else:
			warning("No flows")
	#
	@property
	def logged_volume(self):
		try:
			return self.log_attributes['MMVolume']
		except:
			return self.get_total_volume()
	def get_total_volume(self, ignored_classes=['Noise', 'Duplicate', 'Unclassified']):
		return sum(e.Volume for e in self.events if e.Class not in ignored_classes)
	#
	@property
	def begins(self):
		try:
			return self.log_attributes['LogStartTime']
		except:
			return self.flows[0].DateTimeStamp
			#return self.events[0].StartTime
	@property
	def ends(self):
		try:
			return self.log_attributes['LogEndTime']
		except:
			return self.flows[-1].DateTimeStamp+self.log_attributes['StorageInterval']
			#return self.events[-1].StartTime+self.events[-1].Duration
	def print_summary(self):
		print "%d-field events, %d fixture profiles, %d log attributes" % (len(self.attributes), len(self.fixture_profiles), len(self.log_attributes))
		print "%d events, %d flows between %s and %s" % (len(self.events), len(self.flows), self.begins, self.ends)
	def print_long_summary(self):
		self.print_summary()
		print
		print "Attributes:"
		for n, l in enumerate(self.attributes):
			print '\t', n, l
		if self.has_fixture_profile_section:
			print "Fixture profiles:"
			for n, l in enumerate(self.fixture_profiles):
				print '\t', n, l
		print "Log attributes:"
		if self.has_log_attribute_section:
			for k, v in sorted(self.log_attributes.iteritems()):
				print '\t', k, v
		print "Volume by day:"
		total = self.logged_volume
		for d, ef in self.get_events_by_day():
			daily_total = sum(e.Volume for (e, f) in ef)
			print d, daily_total, self.events_units, "(%5.1f%%)" % (100*daily_total/total)
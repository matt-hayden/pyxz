from collections import namedtuple
from datetime import timedelta
from itertools import groupby
from logging import debug, info, warning, error, critical

default_storage_interval = timedelta(seconds = 10)
ratedata_t = float
volume_t = float

def EventRow_midpoint(e):
	return e.StartTime+e.Duration/2
Interval = namedtuple('Interval', 'min max')

class MeterMaster_Common:
	logged_volume_tolerance = 0.025 # percent diff
	warning_flows_table_duration_tolerance = timedelta(hours=1)
	#
	label = ''
	#
	def _check_log_attributes(self, check_volume = False):
		storage_interval_delta = self.log_attributes['NumberOfIntervals']*self.storage_interval
		flows_table_duration = self.ends - self.begins
		d = flows_table_duration - storage_interval_delta
		if abs(d) > self.warning_flows_table_duration_tolerance:
			warning("Difference of %s between MMData and NumberOfIntervals" % d)
		#
		if check_volume:
			rdv = self.get_total_volume()
			vol_diff = self.logged_volume-rdv
			pct_diff = rdv/self.logged_volume
			if abs(1-pct_diff) > self.logged_volume_tolerance:
				error("Difference of %f %s exceeds %f percent" %
					  (vol_diff, self.flow_units, self.logged_volume_tolerance))
	#
	@property
	def flow_multiplier(self):
		# identical to MM4
		try:
			#m = self.log_attributes['StorageInterval'].seconds/60.0
			m = self.storage_interval.total_seconds()/60.0
			if m > 0:
				return m
		except:
			warning("Bad or unset storage interval")
			return (10.0/60.0)
	@property
	def volume_units(self):
		try:
			return self.log_attributes['Unit']
		except:
			return 'Gallons'
	@property
	def flows_units(self):
		return self.volume_units+"/minute"
	def get_flows_by_day(self):
		FlowDay = namedtuple('FlowDay', 'day flows')
		for d, f in groupby(self.flows, key=lambda f: f.DateTimeStamp.date()):
			yield FlowDay(d, tuple(f))
	@property
	def logged_volume(self):
		try:
			return volume_t(self.log_attributes['MMVolume'])
		except:
			return self.get_total_volume()
	def get_total_volume(self, limit = None):
		if limit is None:
			return self.flow_multiplier*sum(f.RateData for f in self.flows)
		else:
			return self.flow_multiplier*sum(f.RateData for f in self.flows if f.RateData < limit)
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
			return self.flows[-1].DateTimeStamp+self.storage_interval
			#return self.flows[-1].DateTimeStamp+self.log_attributes['StorageInterval']
			#return self.events[-1].StartTime+self.events[-1].Duration
	@property
	def timespan(self):
		return Interval(self.begins, self.ends)
	@property
	def readings(self):
		return Interval(self.log_attributes['BeginReading'], self.log_attributes['EndReading']) 
	def __repr__(self):
		s = " ".join((self.__class__.__name__,
					  "(format '%s')" % self.format if self.format else '',
					  "'%s'" % self.label))
		return "<%s>" % s.strip()
	def print_summary(self):
		print "%d log attributes" % (len(self.log_attributes))
		print "%d flows between %s and %s" % (len(self.flows), self.begins, self.ends)
class TraceWizard_Common(MeterMaster_Common):
	event_table_name = 'events'
	#
	def _check_log_attributes(self):
		MeterMaster_Common._check_log_attributes(self) # yuck
		# These checks are similar to MeterMaster4:
		storage_interval_delta = self.log_attributes['NumberOfIntervals']*self.storage_interval
		d = self.log_attributes['TotalTime'] - storage_interval_delta
		if d:
			warning("Difference of %s between TotalTime and NumberOfIntervals" % d)
		# also check against LogStartTime and LogEndTime, which are not in MeterMaster4_CSV:
		timestamp_delta = self.log_attributes['LogEndTime'] - self.log_attributes['LogStartTime']
		d = timestamp_delta - storage_interval_delta
		if d:
			warning("Difference of %s between LogEndTime and NumberOfIntervals" % d)
	#
	def get_events_and_flows(self):
		"""
		Returns an iterable of the following structure:
			[ event, [flow_0, ..., flow_n]]
		To discern the fields in event or flows, use the flows_header and 
		events_header members.
		TODO: make sure the EventID matches the FlowID (right now these are simply aligned)
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
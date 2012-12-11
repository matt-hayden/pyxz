from collections import namedtuple
from datetime import date, datetime, time, timedelta
from itertools import groupby
from logging import debug, info, warning, error, critical

default_storage_interval = timedelta(seconds = 10)
ratedata_t = float
volume_t = float

def EventRow_midpoint(e):
	return e.StartTime+e.Duration/2
Interval = namedtuple('Interval', 'min max')

class MeterMaster_Common:
	format = ''
	logged_volume_tolerance = 0.025 # percent diff
	sane_storage_intervals = Interval(1,600)
	warning_flows_table_duration_tolerance = timedelta(hours=1)
	#
	#label = ''
	#
	def _check_log_attributes(self, check_volume = False):
		si = self.storage_interval.total_seconds()
		if (si < self.sane_storage_intervals.min):
			self.storage_interval = default_storage_interval
			error("Insane storage interval of %s, defaulting to %s" % (si, self.storage_interval))
		if (si > self.sane_storage_intervals.max):
			self.storage_interval = default_storage_interval
			error("Insane storage interval of %s, defaulting to %s" % (si, self.storage_interval))
		#
		storage_interval_delta = self.log_attributes['NumberOfIntervals']*self.storage_interval
		flows_table_duration = self.ends - self.begins
		d = flows_table_duration - storage_interval_delta
		if abs(d) > self.warning_flows_table_duration_tolerance:
			warning("Difference of %s between flow table and expected NumberOfIntervals" % d)
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
	def get_nutation_rate(self):
		try:
			return self.logged_volume/int(self.log_attributes['TotalPulses'])
		except:
			return None
	@property
	def logged_volume(self):
		try:
			return volume_t(self.log_attributes['MMVolume'])
		except:
			return self.get_total_volume()
	def get_total_volume(self, logical = False, **kwargs):
		# overloaded by subclasses that have events
		return self.flow_multiplier*sum(f.RateData for f in (self.get_logical_flows() if logical else self.flows))
	@property
	def begins(self):
		try:
			return self.log_attributes['LogStartTime']
		except:
			return self.flows[0].DateTimeStamp
	@property
	def ends(self):
		try:
			return self.log_attributes['LogEndTime']
		except:
			return self.flows[-1].DateTimeStamp+self.storage_interval
	def get_complete_days(self, **kwargs):
		midnight = kwargs.pop('midnight', time())
		typer = kwargs.pop('typer', date)
		begin_date, end_date = self.begins.date(), self.ends.date()
		if (self.begins.hour > 6):
			begin_date += timedelta(days=1)
		if (self.ends.hour > 21):
			end_date += timedelta(days=1)
		# convert to datetime rather than date objects:
		if type(begin_date) != typer:
			begin_date = typer.combine(begin_date, midnight)
		if type(end_date) != typer:
			end_date = typer.combine(end_date, midnight)
		return Interval(begin_date, end_date)
	def get_logical_flows(self, **kwargs):
		limit = kwargs.pop('limit', None)
		limit_replacement_value = kwargs.pop('limit_replacement_value', 0)
		begin_ts, end_ts = self.get_complete_days(typer = datetime)
		if limit is None:
			for f in self.flows:
				if (begin_ts <= f.DateTimeStamp <= end_ts):
					yield f
		else:
			for f in self.flows:
				if (begin_ts <= f.DateTimeStamp <= end_ts):
					yield f if (0 <= f.RateData < limit) else limit_replacement_value
	@property
	def duration(self):
		"""
		Use t.duration.days to get the number of days
		"""
		return self.ends - self.begins
	@property
	def days(self):
		return self.duration.days
	@property
	def timespan(self):
		return Interval(self.begins, self.ends)
	@property
	def readings(self):
		return Interval(self.log_attributes['BeginReading'], self.log_attributes['EndReading'])
	def get_register_volume(self, raw = False):
		if raw:
			return self.log_attributes['EndReading'] - self.log_attributes['BeginReading']
		else:
			return self.log_attributes['RegVolume']
	def __repr__(self):
		s = " ".join((self.__class__.__name__,
					  "'%s'" % self.label,
					  "(format '%s')" % self.format if self.format else ''
					  ))
		return "<%s>" % s.strip()
	def print_summary(self):
		print "%d log attributes" % (len(self.log_attributes))
		print "%d flows over %s days" % (len(self.flows), self.days)
class TraceWizard_Common(MeterMaster_Common):
	event_table_name = 'events'
	cyclers = [ 'Clotheswasher', 'Dishwasher', 'Clothes Washer', 'Dish Washer' ]
	cyclers = [ s.upper() for s in cyclers ]
	#
	@property
	def fixture_names(self):
		# Should be overloaded by subclasses
		return set(e.Class for e in self.events)
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
	def get_events_by_day(self, logical = True, **kwargs):
		"""
		Returns all events broken into 24-hour periods. Events spanning
		midnight are, by default, not broken across days. Returns:
			[ (date0, [event_00, ..., event_0n]) ... ]
		"""
		day_decider = kwargs.pop('day_decider', None)
		if not day_decider:
			def day_decider(e):
				#return EventRow_midpoint(e).date()
				return e.StartTime.date()
		if logical:
			b, e = self.get_complete_days(typer=date)
			for d, ef in groupby(self.get_logical_events(**kwargs) if logical else self.events, key=day_decider):
				if (b <= d < e): # note this is a date comparison, not datetime, hence < instead of <=
					yield (d, tuple(ef))
		else:
			for d, ef in groupby(self.events, key=day_decider):
				yield (d, tuple(ef))
	def get_events_and_flows(self, logical = True, **kwargs):
		"""
		Returns an iterable of the following structure:
			[ event, [flow_0, ..., flow_n]]
		To discern the fields in event or flows, use the flows_header and 
		events_header members.
		Note that in the events and flows members, EventID may not exactly 
		correspond to an event's order in those lists. This method works around
		that.
		"""
		event_key = kwargs.pop('event_key', lambda e: e.EventID)
		flow_key = kwargs.pop('flow_key', lambda e: e.EventID)
		#
		size = event_key(self.events[-1])+1
		#size = max([event_key(e) for e in self.events])+1 # if not sorted
		#
		el = [None,]*size
		fl = [None,]*size
		missed_flows = []
		for row in self.get_logical_events(**kwargs) if logical else self.events:
			k=event_key(row)
			if k is not None:
				el[k] = row
			else:
				critical("Error reading ID from event %s" % str(row))
		for k, fs in groupby(self.flows, flow_key):
			if el[k]:
				yield el[k], list(fs)
			else:
				missed_flows.extend(fs)
		info("%d flows match no event" %len(missed_flows)+("(probably because events from incomplete days are removed)" if logical else ""))
	def get_events_and_rates(self, **kwargs):
		"""
		Returns an iterable of the following structure:
			[ event, [rate_0, ..., rate_n]]
		To discern the fields in event, use events_header. The units of flow
		rate are available in the flows_units member.
		"""
		for e, fs in self.get_events_and_flows(**kwargs):
			yield e, tuple(f.RateData for f in fs)
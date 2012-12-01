from collections import namedtuple
from datetime import timedelta
from itertools import groupby

Interval = namedtuple('Interval', 'min max')

class MeterMaster_Common:
	default_flow_multiplier = 10.0/60.0
	logged_volume_tolerance = 0.025 # percent diff
	warning_flows_table_duration_tolerance = timedelta(hours=1)
	#
	@property
	def flow_multiplier(self):
		# identical to MM4
		try:
			m = self.log_attributes['StorageInterval'].seconds/60.0
			if m > 0:
				return m
		except:
			warning("Bad storage interval; defaulting to %s.",
					self.default_flow_multiplier)
		return self.default_flow_multiplier
	@property
	def volume_units(self):
		return self.log_attributes['Unit']
	@property
	def flows_units(self):
		return self.volume_units+"/minute"
	def get_flows_by_day(self):
		FlowDay = namedtuple('FlowDay', 'day flows')
		for d, f in groupby(self.flows, key=lambda f: f.DateTimeStamp.date()):
			yield FlowDay(d, tuple(f))
	@property
	def logged_volume(self):
		return self.log_attributes['MMVolume']
	def get_total_volume(self, limit = None):
		if limit is None:
			return self.flow_multiplier*sum(f.RateData for f in self.flows)
		else:
			return self.flow_multiplier*sum(f.RateData for f in self.flows if f.RateData < limit)
	@property
	def timespan(self):
		try:
			return Interval(self.flows[0].DateTimeStamp,
							self.flows[-1].DateTimeStamp+self.log_attributes['StorageInterval'])
		except:
			return None
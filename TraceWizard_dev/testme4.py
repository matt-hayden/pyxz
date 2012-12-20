#import logging
import os
import sys

from datetime import datetime, date, time, timedelta
from glob import glob
from itertools import groupby, izip
from logging import debug, info, warning, error, critical

from pandas import date_range, Series
try:
	from pytz import timezone
except:
	pass
#import numpy as np
#import yaml

from TraceWizard5 import load_config, open_file, volume_t
class Base1:
	def copy_attr_from(self, obj, m = '*'):
		try:
			setattr(self, m, getattr(obj, m))
			return True
		except:
			#setattr(self, m, None)
			return False
class Analyzer(Base1):
	def __init__(self, data, **kwargs):
		self.from_file(data, **kwargs)
	def from_file(self, data, **kwargs):
		tz = kwargs.pop('tz', None)
		if type(tz) == str:
			tz = timezone(tz)
		input_trace = open_file(data, **kwargs)
		#
		# Copy members:
		for m in ['format', 'version', 'log_attributes', 'meter_info', 'label']:
			self.copy_attr_from(input_trace, m)
		#self.log_attributes = input_trace.log_attributes
		#self.label = input_trace.label
		#
		if input_trace.has_flows:
			storage_interval = input_trace.storage_interval
			freq = "%ds" % storage_interval.total_seconds()
			r = date_range(start=input_trace.begins, end=input_trace.ends, freq=freq, tz=tz)
			print input_trace.flows[0], input_trace.flows[-1], "should match:"
			print min(f.DateTimeStamp for f in input_trace.flows), max(f.DateTimeStamp for f in input_trace.flows)
			print r
			print "Input:", len(input_trace.flows), "flows"
			self.flows = Series(index=r)
			for f in input_trace.flows:
				self.flows[f.DateTimeStamp] = f.RateData
			if __debug__:
				self.flows.describe()
		#if input_trace.has_events:
	@property
	def nonzero_flows(self):
		return self.flows.dropna()

if __name__ == '__main__':
	import os.path
	
	# Load the config file:
	config = load_config("TraceWizard_config.py")
	fixture_type_lookup = config.fixture_type_lookup
	fixtures = config.AllFixtures
	cyclers = config.FirstCycleFixtures
	ftypes = set(fixture_type_lookup.values())
	#window_size = config.window_size
	#
	tempdir=os.path.expandvars('%TEMP%\example-traces')
	#filename = os.path.join(tempdir, '12S704.twdb')
	filename = os.path.join(tempdir, '67096.tdb')
	t = Analyzer(filename)
	t.flows.hist()
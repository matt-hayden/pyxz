from collections import namedtuple
from datetime import timedelta
from itertools import groupby
from logging import debug, info, warning, error, critical

from MDB_File import MDB_File
from MeterMaster_Common import MeterMaster_Common, Interval

class MeterMaster3_Error(Exception):
	pass
class MeterMaster3_MDB(MeterMaster_Common):
	#
	def __init__(self, data, load = True, **kwargs):
		self.filename = None
		if type(data) == str:
			if os.path.exists(data):
				if load:
					self.from_file(data)
				else:
					self.filename = data
			elif os.path.exists(os.path.split(data)[0]):	# stub for write implementation
				self.filename = data
			elif load:
				self.from_query(data)
		#else:
		#	self.from_iterable(data)
	def from_file(self,
				  filename,
				  load_data = True,
				  load_headers = True,
				  driver_name = None
				  ):
		self.filename = filename
		db = MDB_File(filename, driver_name)
		self.format = "MDB (%s)" % db.driver_name
		if load_data:
			self.flows = list(db.generate_table('MMData'))
			if len(self.flows) > 0:
				info("%d flow data points" % len(self.flows))
			else:
				critical("No flow data points loaded")
		if load_headers:
			d = {}
			t = db.generate_table('Customer')
			d.update(self.CustomerRowDict(t[0]))
			t = db.generate_table('MeterInfo')
			d.update(self.MeterInfoRowDict(t[0]))
			#
			self.define_log_attributes(d)
	#
if __name__ == '__main__':
	import logging
	import os.path
	#
	logging.basicConfig(level=logging.INFO)
	#
	#desktop=os.path.expandvars('%UserProfile%\Desktop')
	tempdir=os.path.expandvars('%TEMP%\example-traces')
	fn = os.path.join(tempdir, '67096.MDB')
	print "Using", fn, "(%s)" % ("found" if os.path.exists(fn) else "not found")
	m = MeterMaster3_MDB(fn)
	print m
	for d, fs in m.get_flows_by_day():
		print d, sum([ f.RateData for f in fs ])*m.flow_multiplier
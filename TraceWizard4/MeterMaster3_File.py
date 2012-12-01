from collections import namedtuple
from datetime import timedelta
from itertools import groupby
from logging import debug, info, warning, error, critical

from MDB_File import MDB_File
from MeterMaster_Common import MeterMaster_Common, Interval

class MeterMaster3_MDB(MeterMaster_Common):
	#
	@staticmethod
	def CustomerRowDict(row):
		d = {}
		d['Address'] = row.Address.strip()
		d['City'] = row.City.strip()
		d['CustomerID'] = row.CustomerID.strip()
		d['CustomerName'] = row.CustomerName.strip()
		d['Note'] = row.Note.strip()
		d['PhoneNumber'] = row.PhoneNumber.strip()
		d['PostalCode'] = row.PostalCode.strip()
		d['State'] = row.State.strip()
		return d
	@staticmethod
	def MeterInfoRowDict(row):
		# member names are case-sensitive in adodbapi
		d = {}
		d['BeginReading'] = row.BeginReading
		d['CombinedFile'] = row.CombinedFile
		d['ConvFactor'] = row.ConvFactor
		d['ConvFactorType'] = row.ConvFactorType
		d['DatabaseMultiplier'] = row.DatabaseMultiplier
		d['EndReading'] = row.EndReading
		d['LED'] = row.LED
		d['Make'] = row.Make.strip()
		d['MeterCode'] = row.MeterCode
		d['MMVolume'] = row.MMVolume
		d['Model'] = row.Model.strip()
		d['NumberOfIntervals'] = row.NumberOfIntervals
		d['Nutation'] = row.Nutation
		d['RegVolume'] = row.RegVolume
		d['Size'] = row.Size.strip()
		d['StorageInterval'] = timedelta(seconds=row.StorageInterval)
		d['TotalPulses'] = row.TotalPulses
		d['Unit'] = row.Unit.strip()
		return d
	#
	def __init__(self, data):
		self.from_file(data)
	def __init__(self, data, load = True):
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
		else:
			self.from_iterable(data)
	def from_file(self, filename, load_data = True, load_headers = True, driver_name = None):
		self.filename = filename
		db = MDB_File(filename, driver_name)
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
	def define_log_attributes(self, pairs):
		if type(pairs) == dict:
			self.log_attributes = pairs
		else:
			#self.log_attributes = dict([format_log_attribute(k,v) for k,v in pairs if k not in (None,'')])
			self.log_attributes = dict(pairs)
		debug("%d datalogger attributes" % len(self.log_attributes))
		# Not very similar to MeterMaster4:
		try:
			storage_interval_delta = self.log_attributes['NumberOfIntervals']*self.log_attributes['StorageInterval']
			t = self.timespan
			if t:
				flows_table_duration = t[-1] - t[0]
				d = flows_table_duration - storage_interval_delta
				if abs(d) > self.warning_flows_table_duration_tolerance:
					warning("Difference of %s between MMData and NumberOfIntervals",
							d)
			#
			rdv = self.get_total_volume()
			vol_diff = self.logged_volume-rdv
			pct_diff = rdv/self.logged_volume
			if abs(1-pct_diff) > self.logged_volume_tolerance:
				error("Difference of %f %s exceeds %f percent" %
					  (vol_diff, self.flow_units, self.logged_volume_tolerance))
		except Exception as e:
			error("Flows table error: %s" % e)


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
	print m.log_attributes
	for d, fs in m.get_flows_by_day():
		print d, sum([ f.RateData for f in fs ])*m.flow_multiplier
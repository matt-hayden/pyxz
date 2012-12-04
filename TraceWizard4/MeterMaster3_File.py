from collections import namedtuple
from datetime import timedelta
from itertools import groupby
from logging import debug, info, warning, error, critical

from MDB_File import MDB_File
from MeterMaster_Common import MeterMaster_Common, Interval, ratedata_t, volume_t


def format_MeterMaster3_Customer_header(row):
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
def format_MeterMaster3_MeterInfo_header(row):
	# member names are case-sensitive in adodbapi
	d = {}
	d['BeginReading'] = volume_t(row.BeginReading)
	d['CombinedFile'] = row.CombinedFile
	d['ConvFactor'] = float(row.ConvFactor)
	d['ConvFactorType'] = row.ConvFactorType
	d['DatabaseMultiplier'] = row.DatabaseMultiplier
	d['EndReading'] = volume_t(row.EndReading)
	d['LED'] = row.LED
	d['Make'] = row.Make.strip()
	d['MeterCode'] = row.MeterCode
	d['MMVolume'] = volume_t(row.MMVolume)
	d['Model'] = row.Model.strip()
	d['NumberOfIntervals'] = int(row.NumberOfIntervals)
	d['Nutation'] = row.Nutation
	d['RegVolume'] = volume_t(row.RegVolume)
	d['Size'] = row.Size.strip()
	d['StorageInterval'] = timedelta(seconds=row.StorageInterval)
	#d['StorageInterval'] = row.StorageInterval
	d['TotalPulses'] = int(row.TotalPulses)
	d['Unit'] = row.Unit.strip()
	return d

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
			d.update(format_MeterMaster3_Customer_header(t[0]))
			t = db.generate_table('MeterInfo')
			d.update(format_MeterMaster3_MeterInfo_header(t[0]))
			#
			self.define_log_attributes(d)
			self._check_log_attributes()
	def define_log_attributes(self, pairs):
		if type(pairs) == dict:
			self.log_attributes = pairs
		else:
			self.log_attributes = dict(pairs)
		debug("%d datalogger attributes" % len(self.log_attributes))
		#
		self.storage_interval = self.log_attributes['StorageInterval']
		#
		n = self.log_attributes['CustomerID']
		if not n:
			try:
				fn = os.path.split(self.filename)[-1]
				n = os.path.splitext(fn)[0]
			except:
				n = "<%s>" % self.__class__.__name__
		self.label = n
		#
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
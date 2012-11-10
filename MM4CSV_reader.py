#! /usr/bin/env python
import csv
from datetime import datetime
import re
#import itertools

#import numpy as np
timestamp_regex = re.compile('[0-1]?\d/\d{1,2}/\d{2,4} [0-2]\d:\d{2}(:\d{2}) (am|AM|pm|PM)?')

class MM4CSV_Abstract:
	datasection_header = 'DateTimeStamp,RateData'
	ignore_empty_attributes = False
	max_header_rows=50 # stop if too many header rows are encountered
	#
	def __init__(self, filename = None):
		self.attributes = {}
		self.datapoints = []
		if filename:
			self.from_file(filename)
	def set_attribute(self, name, value):
		"""
		override this if you want to handle any attributes specially, such as 
		type conversion or ignoring blanks.
		"""
		if name:
			self.attributes[name] = value
	def set_datapoint(self, timestamp, rawdata=None, ratedata=None):
		"""
		Override this for better storage or analysis of individual data points.
		"""
		self.datapoints.append((timestamp, rawdata, ratedata))
	def from_file(self, filename):
		with open(filename) as fi:
			self.from_iterable(fi)
	def from_iterable(self, iterable):
		self.header = list(self.get_header_lines(iterable))
		errors = [ self.set_datapoint(timestamp, None, value) for timestamp, value in csv.reader(iterable) ]
		errors = [ self.set_attribute(name, value) for name, value in csv.reader(self.header) ]
	def get_header_lines(self, fi):
		for line_no, line in enumerate(fi):
			line = line.strip()
			if line == self.datasection_header:
				self.header_rows = line_no+1
				break
			elif line_no > self.max_header_rows:
				raise ValueError("parsing header stopped: more than %d rows encountered" % self.max_header_rows)
			else:
				yield line
		# iterating on fi here would start pulling in data
#
class MM4CSV_File(MM4CSV_Abstract):
	timestamp_format = '%m/%d/%Y %I:%M:%S %p'
	ratedata_t = float
	def set_datapoint(self, timestamp, rawdata=None, ratedata=None):
		"""
		Override this for better storage or analysis of individual data points.
		"""
		self.datapoints.append((datetime.strptime(timestamp, self.timestamp_format),
								rawdata, 
								self.ratedata_t(ratedata) ))
#
if __name__ == '__main__':
	mf = MM4CSV_File(r'F:\Documents and Settings\Matt Hayden\Desktop\12S704.csv')
	#reader = csv.reader(mf.header_text)
	#for row in reader:
	#	print row
	print mf.header
	print mf.attributes
	print len(mf.datapoints), "data points like", mf.datapoints[0]
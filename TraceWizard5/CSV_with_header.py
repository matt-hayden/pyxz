from contextlib import closing
import csv
import os.path
from cStringIO import StringIO

class CSV_with_header:
	data_table_name = 'data'
	end_of_header = ''
	max_header_rows=25 # stop if too many header rows are encountered
	#
	def __init__(self, data = None, eoh = None, load = True):
		if eoh is not None:
			self.end_of_header = eoh
		if data:
			if type(data) == str:
				if load and os.path.exists(data):
					self.from_file(data)
				elif os.path.exists(os.path.split(data)[0]): # stub
					self.filename = data
				else:
					self.from_iterable(data)
			else:
				self.from_iterable(data)
	def from_file(self, filename):
		with open(filename) as fi:
			self.from_iterable(fi)
		self.filename = filename
	def from_iterable(self, iterable):
		self.parse_CSV(iterable)
		self.filename = None
	def parse_CSV_header(self, iterable = None):
		iterable = iterable or open(self.filename)
		with closing(StringIO()) as sio:
			for line_number, line in enumerate(iterable, start=1):
				#line = line.strip()
				if line == self.end_of_header:
					#self.header_rows = line_number+1
					break
				elif line_number > self.max_header_rows:
					raise ValueError("parsing header stopped: more than %d rows encountered" % self.max_header_rows)
				else:
					sio.write(line)
			sio.seek(0)
			self.header = list(csv.reader(sio))
		return line_number #+1?
	def parse_CSV(self, iterable = None):
		"""
		Use this as a pattern to be overridden in subclasses.
		"""
		iterable = iterable or open(self.filename)
		line_number = self.header_lines = self.parse_CSV_header(iterable)
		self.__dict__[self.data_table_name] = list(csv.reader(iterable))
#
if __name__ == '__main__':
	import os.path
	#desktop=os.path.expandvars('%UserProfile%\Desktop')
	tempdir=os.path.expandvars('%TEMP%\example-traces')
	fn = os.path.join(tempdir, '12S704.csv')
	print fn, "found:", os.path.exists(fn)
	m = CSV_with_header(fn, eoh='DateTimeStamp,RateData\n')
	
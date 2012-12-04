from contextlib import closing
import csv
import os, os.path
import re
from cStringIO import StringIO

class CSV_with_header:
	"""
	Reads a CSV file that contains a special header section, separated from an
	arbitrary body. The seperator can be a string, or a fixed number of rows:
	
	>>> CSV_with_header(filename, "#EOH")
	would read in the file up to #EOH, possibly erroring if reaching an
	unreasonable number of rows without #EOH.
	
	>>> CSV_with_header(filename, rows = 3)
	would read the first 3 rows, or up to the first blank line.
	
	The easiest use is to subclass CSV_with_header and implement a parse_CSV()
	function, which takes an iterable. If you don't subclass, the body of the
	parsed file is available in the list of rows in the member body.
	"""
	eoh = os.linesep					#
	error_when_max_rows_reached = True	#
	max_header_rows=25					#
	#
	def __init__(self, 
				 data = None, 
				 eoh = None, 
				 rows = None,
				 load = True):
		if eoh is not None:
			self.end_of_header = eoh
		elif rows:
			# mode should be 'quiet when maxrows reached'
			self.error_when_max_rows_reached = False
			self.max_header_rows = rows
		#
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
				if (line_number > self.max_header_rows):
					if self.error_when_max_rows_reached:
						raise ValueError("parsing header stopped: more than %d rows encountered" % self.max_header_rows)
				elif line == self.end_of_header:
					break
				else:
					sio.write(line)
			sio.seek(0)
			self.header = list(csv.reader(sio))
			self.header_lines = line_number
		return line_number
	def parse_CSV(self,
				  iterable = None,
				  data_table_name = 'body'
				  ):
		"""
		Use this as a pattern to be overridden in subclasses. The member name
		specified in data_table_name is used only for example.
		"""
		iterable = iterable or open(self.filename)
		line_number = self.parse_CSV_header(iterable)
		self.__dict__[data_table_name] = list(csv.reader(iterable))
class CSV_with_header_and_version(CSV_with_header):
	format = 'CSV' # subclasses should override this
	version_regex = re.compile('[vV]?(?P<version_string>[\d.]*\d)')
	def parse_CSV_header(self, iterable = None):
		line_number = CSV_with_header.parse_CSV_header(self, iterable) # yuck
		if self.header[0][0] == self.format:
			try:
				self.version = self.header[0][1]
				try:
					m = self.version_regex.match(self.version)
					if m:
						self.version_tuple = tuple(m.group('version_string').split('.'))
						self.header = self.header[1:]
				except:
					pass
			except:
				self.version = None
		return line_number
#
if __name__ == '__main__':
	import os.path
	#desktop=os.path.expandvars('%UserProfile%\Desktop')
	tempdir=os.path.expandvars('%TEMP%\example-traces')
	fn = os.path.join(tempdir, '12S704.csv')
	print fn, "found:", os.path.exists(fn)
	# Example 1: read the whole file
	# m = CSV_with_header(fn, eoh='DateTimeStamp,RateData\n')
	# Example 2: read only the headers
	m = CSV_with_header_and_version(fn, eoh='DateTimeStamp,RateData\n', load=False)
	print "Parsing header:"
	m.parse_CSV_header()
	print m.header_lines, "rows in header"
	print m.header
	print m.format, m.version
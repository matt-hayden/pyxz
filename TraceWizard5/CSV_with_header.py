from contextlib import closing
import csv
import io
import os, os.path
import re
from cStringIO import StringIO
from zipfile import ZipFile

class SelfNamedZipFileError(Exception):
	pass
def SelfNamedZipFile(filepath, default_extensions = [], **kwargs):
	with ZipFile(filepath, 'r') as zi:
		filelist = zi.infolist()
		if len(filelist) == 0:
			raise SelfNamedZipFileError("File '{}' empty".format(filepath))
		elif 'zip_entry' in kwargs: # can be a filename or ZipInfo object
			bi = zi.open(kwargs.pop('zip_entry'))
		elif len(filelist) == 1:
			bi = zi.open(filelist[0])
		else:
			dirname, filename = os.path.split(filepath)
			basename, ext = os.path.splitext(filename)
			default_filenames = [basename]+[ basename+ext for ext in default_extensions ]
			default_filenames = [ f.upper() for f in default_filenames ]
			possible_valid_entries = [ i for i in filelist if i.filename.upper() in default_filenames ]
			if len(possible_valid_entries) == 1:
				bi = zi.open(possible_valid_entries[0])
			else:
				print "%d possible files: %s" %(len(possible_valid_entries), ", ".join(possible_valid_entries))
				print "Opening first occurring in '%s'" %(filename)
				bi = zi.open(filelist[0])
		return io.TextIOWrapper(bi, newline=None)

class CSV_with_header_Error(Exception):
	pass
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
	def __init__(self, data, *args, **kwargs):
		eoh = kwargs.pop('eoh', None)
		rows = kwargs.pop('rows', None)
		load = kwargs.pop('load', True)
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
						self.from_file(data, **kwargs)
					else:
						self.path = data
				elif os.path.exists(os.path.dirname(data)):	# stub for write implementation
					self.path = data
				else: # assume this is a long string from a CSV format file
					self.from_iterable(data, **kwargs)
			else:
				self.from_iterable(data, **kwargs)
	def from_file(self, filepath, **kwargs):
		dirname, filename = os.path.split(filepath)
		basename, ext = os.path.splitext(filename)
		with SelfNamedZipFile(filepath, default_extensions = ('.CSV',), **kwargs) if kwargs.pop('force_unzip', ext.upper() == '.ZIP') else open(filepath) as fi:
			self.from_iterable(fi, **kwargs)
		self.path = filepath
	def from_iterable(self, iterable, **kwargs):
		self.parse_CSV(iterable, **kwargs)
		self.path = None
	def parse_CSV_header(self, iterable = None):
		iterable = iterable or open(self.path)
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
		self.has_header = True
		return line_number
	def parse_CSV(self,
				  iterable = None,
				  data_table_name = 'body'
				  ):
		"""
		Use this as a pattern to be overridden in subclasses. The member name
		specified in data_table_name is used only for example.
		"""
		iterable = iterable or open(self.path)
		line_number = self.parse_CSV_header(iterable)
		self.__dict__[data_table_name] = list(csv.reader(iterable))
class CSV_with_header_and_version(CSV_with_header):
	format = 'CSV' # subclasses should override this, see below
	version_regex = re.compile('[vV]?(?P<version_string>[\d.]*\d)')
	def parse_CSV_header(self, iterable = None):
		line_number = CSV_with_header.parse_CSV_header(self, iterable) # yuck
		if not self.header[0][0].upper().startswith(self.format.upper()):
			raise CSV_with_header_Error("'%s' not first line in header (%s)" % (self.format, self.header[0][0]))
		try:
			self.version = self.header[0][1:]
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
	class tester(CSV_with_header_and_version):
		format = 'MM100 Data Export' # for testing
	#desktop=os.path.expandvars('%UserProfile%\Desktop')
	tempdir=os.path.expandvars('%TEMP%\example-traces')
	fn = os.path.join(tempdir, '12S704.csv')
	print fn, "found:", os.path.exists(fn)
	# Example 1: read the whole file
	# m = CSV_with_header(fn, eoh='DateTimeStamp,RateData\n')
	# Example 2: read only the headers
	m = tester(fn, eoh='DateTimeStamp,RateData\n', load=False)
	print "Parsing header:"
	m.parse_CSV_header()
	print m.header_lines, "rows in header"
	print m.header
	print m.format, m.version
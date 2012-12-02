from collections import namedtuple
from contextlib import closing
import csv
from datetime import datetime
import re
from cStringIO import StringIO

dequote_regex=re.compile('\\s*(["\'])(.*)\\1\\s*')
def dequote(text):
	m = dequote_regex.match(text)
	return m.groups()[-1] if m else text

Java_time_format_lookup = {
	'''yyyy-MM-dd'T'HH:mm:ss''':	'%Y-%m-%dT%H:%M:%S',
	"yyyy-MM-dd HH:mm:ss":			'%Y-%m-%d %H:%M:%S'
	}

class ARFF_format:
	"""
	Missing values and relational attributes are not supported.
	"""
	attribute_section_regex=re.compile('@RELATION\s+(?P<relation_name>.*)\s*', re.IGNORECASE)
	attribute_regex=re.compile('@ATTRIBUTE\s+(?P<attribute_name>\w+)\s+(?P<attribute_parameters>.*)\s*', re.IGNORECASE)
	attribute_parameter_regex=re.compile('(?P<datatype>NUMERIC|INTEGER|REAL|\{(?P<nominal_spec>.*)\}|STRING|DATE|RELATIONAL)(\s+(?P<format>.*))?', re.I)
	comment_regex=re.compile('%\s*(?P<comment>.*)')
	data_section_regex=re.compile('@DATA', re.IGNORECASE)
	#
	ARFF_Attribute = namedtuple('ARFF_Attribute', 'Name Type Formatter Values')
	class AttributeError(Exception):
		pass
	@staticmethod
	def attribute_name_formatter(s):
		return s.title()
	numeric_t = float
	real_t = float # Decimal?
	bool_sets = [ set(l) for l in [ ['True', 'False'], ['Yes', 'No'] ] ]
	#
	index_nominals = False
	#
	def parse_ARFF_header(self,
						  iterable,
						  line_number = 1,
						  max_lines = 25
						  ):
		"""
		Really just a stub for testing
		"""
		for line_number, line in enumerate(iterable, start=line_number):
			if line_number > max_lines:
				break
			mc = self.comment_regex.match(line)
			if mc:
				print "Comment=", mc.group('comment')
				continue
			mr = self.attribute_section_regex.match(line)
			if mr:
				print "Relation=", mr.group('relation_name')
				break
		self.define_attributes(iterable, line_number)
		return line_number
	def define_attributes(self, 
						  iterable,				# iterable is possibly an open file
						  line_number = 1,		# starting line number
						  max_lines = 255, 		# exits if more than max_lines read
						  next_section = None	# returns null while still in the attribute section
						  ):
		"""
		"""
		if next_section is None:
			next_section = self.data_section_regex.match
		a = []
		max_line_number = line_number+max_lines
		for line_number, line in enumerate(iterable, start=line_number):
			if line_number > max_line_number:
				raise ValueError("More than %d lines encountered" % max_line_number)
			md = next_section(line)
			if md:
				break
			#
			if not line.strip():
				continue
			else:
				mc = self.comment_regex.match(line)
				if mc:
					print "Comment", mc.group('comment')
					continue
			a.append(self.parse_attribute_line(line))
		self.attributes = a
		return line_number
	def parse_attribute_line(self,
							 line,
							 row_factory = None
							 ):
		allowed_values = None
		formatter = None
		if not row_factory:
			row_factory = self.ARFF_Attribute
		#
		m1 = self.attribute_regex.match(line)
		if m1:
			name, p = m1.group('attribute_name'), m1.group('attribute_parameters')
			if self.attribute_name_formatter:
				name = self.attribute_name_formatter(name)
			m2 = self.attribute_parameter_regex.match(p)
			if m2:
				t = m2.group('datatype').upper()
				#
				if t == 'NUMERIC':
					formatter = self.numeric_t
				elif t == 'INTEGER':
					formatter = int
				elif t == 'REAL':
					formatter = self.real_t
				elif t == 'STRING':
					formatter = lambda s: s.strip()
				elif t == 'DATE':
					# note that format comes in as a Java date format string
					f = m2.group('format')
					try:
						f = Java_time_format_lookup[dequote(f)]
					except:
						"Default Java date format string from ARFF specification is yyyy-MM-dd'T'HH:mm:ss"
						f = '''yyyy-MM-dd'T'HH:mm:ss'''
					formatter = lambda s: datetime.strptime(s, f)
				elif t == 'RELATIONAL':
					raise NotImplementedException("%s datatype not implemented" % t)
				else: # assume nominal
					values = m2.group('nominal_spec')
					if values:
						allowed_values = values.split(',')
					else:
						raise ValueError("No nominal attribute spec")
					t = 'NOMINAL'
					if allowed_values:
						if set(allowed_values) in self.bool_sets:
							formatter = bool
						#elif self.index_nominals:
						#	lookup_key = dict((k, i) for i,k in enumerate(allowed_values, start=1))
						#	formatter = lookup_key.get
						else:	
							formatter = None
				#
				return row_factory(name, t, formatter, allowed_values)
			else:
				raise AttributeError("'%s' parsed from '%s' not recognized" % (p, line.strip()) )
		else:
			raise AttributeError("'%s' not recognized" % line.strip())
	# Body parts
	def _get_body_formatters(self, null_function = lambda z:z):
		formatters = [ a.Formatter for a in self.attributes ]
		formatters = [ f if f else null_function for f in formatters ]
		return formatters
	@property
	def body_header(self):
		return [a.Name for a in self.attributes]
	def parse_ARFF_body(self,
						iterable,				# iterable is possibly an open file
						line_number = 1,		# starting line number
						member_name = 'body',	# name of object member to refer to this table
						next_section = None,	# returns null while still in the attribute section
						line_parser = None		# override the row factory return here
						):
		###
		if not line_parser:
			row_factory = namedtuple('ARFF_Row', self.body_header)
			def line_parser(iterable):
				return row_factory(*[ f(a) for f, a in zip(self._get_body_formatters(), iterable) ])
		#parse_body_line = self._get_parse_body_line()
		###
		with closing(StringIO()) as sio:
			if next_section:
				for line_number, line in enumerate(iterable, start=line_number+1):
					# This section has some logic that should be copied below
					n = next_section(line)
					if n:
						break
					# else: #
					if line.strip() and (self.comment_regex.match(line) is None):
						sio.write(line)
			else:
				for line_number, line in enumerate(iterable, start=line_number+1):
					if line.strip() and (self.comment_regex.match(line) is None):
						sio.write(line)
			sio.seek(0)
			self.__dict__[member_name] = [ line_parser(l) for l in csv.reader(sio) ]
		return line_number
	def from_file(self, filename):
		with open(filename) as fi:
			self.from_iterable(fi)
		self.filename = filename
	def from_iterable(self, iterable):
		self.parse_ARFF(iterable)
		self.filename = None
	def parse_ARFF(self, iterable):
		line_number = self.parse_ARFF_header(iterable)
		line_number = self.parse_ARFF_body(iterable, line_number = line_number)
		
class ARFF_format_with_version(ARFF_format):
	header_format_regex=re.compile('%\s*Format:\s*(?P<header_format>.*)')
	header_version_regex=re.compile('%\s?Version:\s*(?P<header_version>.*)')
	#
	@staticmethod
	def sniff_version(iterable,
					  max_lines = 4,
					  start_line = 1,
					  header_version_parser = None
					  ):
		"""
		Returns a tuple like ('File format', (Format version), Number of header lines)
		"""
		if not header_version_parser:
			def header_version_parser(match):
				try:
					version_tuple = tuple(int(d) for d in match.group('header_version').split('.'))
					return version_tuple
				except:
					return None
		#
		next_section=ARFF_format_with_version.attribute_section_regex.match
		for line_number, line in enumerate(iterable, start=start_line):
			if line_number > max_lines:
				return None, None, line_number
			n=next_section(line)
			if n:
				break
			# else:
			m = ARFF_format_with_version.header_format_regex.match(line)
			if m:
				format = m.group('header_format')
				continue
			m = ARFF_format_with_version.header_version_regex.match(line)
			if m:
				version = header_version_parser(m)
				continue
			m = ARFF_format_with_version.comment_regex.match(line)
			#if m and m.group('comment'):
			#	print line_number, line
		return format, version, line_number
if __name__ == '__main__':
	import os.path
	#
	#desktop=os.path.expandvars('%UserProfile%\Desktop')
	tempdir=os.path.expandvars('%TEMP%\example-traces')
	fn = os.path.join(tempdir, 'arff-test.twdb')
	fn = os.path.join(tempdir, '12S704.twdb')
	a = ARFF_format()
	#fi = open(fn).read().split('\n')
	#a.define_attributes(fi[:50])
	with open(fn) as fi:
		#a.define_attributes(fi)
		a.parse_ARFF(fi)
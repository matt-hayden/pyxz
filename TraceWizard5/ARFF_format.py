from collections import namedtuple
from datetime import datetime
import re

dequote_regex=re.compile('\\s*(["\'])(.*)\\1\\s*')
def dequote(text):
	m = dequote_regex.match(text)
	return m.groups()[-1] if m else text

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
	@staticmethod
	def attribute_name_formatter(s):
		return s.title()
	numeric_t = float
	real_t = float # Decimal?
	bool_sets = [ set(l) for l in [ ['True', 'False'], ['Yes', 'No'] ] ]
	#
	index_nominals = False
	#
	def parse_header(self, iterable, line_number = 1, max_lines = 25):
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
	def define_attributes(self, iterable, line_number = 1, max_lines = 255):
		"""
		"""
		a = []
		max_line_number = line_number+max_lines
		for line_number, line in enumerate(iterable, start=line_number):
			if line_number > max_line_number:
				raise ValueError("More than %d lines encountered" % max_line_number)
			md = self.data_section_regex.match(line)
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
	def parse_attribute_line(self,
							 line,
							 row_factory = None
							 ):
		if not row_factory:
			row_factory = self.ARFF_Attribute
		allowed_values = None
		formatter = None
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
					# note that format is a Java date format string
					f = m2.group('format') or '''yyyy-MM-dd'T'HH:mm:ss'''	# default Java date format string from ARFF specification
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
						elif self.index_nominals:
							lookup_key = dict((k, i) for i,k in enumerate(allowed_values, start=1))
							#lookup_label = dict(enumerate(allowed_values))
							formatter = lookup_key.get
						else:	
							formatter = None
				#
				return row_factory(name, t, formatter, allowed_values)
			else:
				print "*** rest of line", p, "not understood"
		else:
			print "'%s' not recognized" % line.strip()
class ARFF_format_with_version(ARFF_format):
	header_format_regex=re.compile('%\s*Format:\s*(?P<header_format>.*)')
	header_version_regex=re.compile('%\s?Version:\s*(?P<header_version>.*)')
	#
	@staticmethod
	def sniff_version(iterable, max_lines = 4, start_line = 1):
		"""
		Returns a tuple like ('File format', (Format version), Number of header lines)
		"""
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
	a = ARFF_format()
	#fi = open(fn).read().split('\n')
	#a.define_attributes(fi[:50])
	with open(fn) as fi:
		#a.define_attributes(fi)
		a.parse_header(fi)
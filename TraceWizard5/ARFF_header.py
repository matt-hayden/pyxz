import re

class ARFF_format:
	comment_regex=re.compile('%\s*(?P<comment>.*)')
	#
	relation_section_regex=re.compile('@RELATION\s+(?P<relation_name>.*)')
	relation_regex=re.compile('@ATTRIBUTE\s+(?P<attribute_name>\w+)\s+(?P<attribute_parameters>.*)')
class ARFF_header(ARFF_format):
	### ARFF statements:
	header_format_regex=re.compile('%\s*Format:\s*(?P<header_format>.*)')
	header_version_regex=re.compile('%\s?Version:\s*(?P<header_version>.*)')
	data_section_regex=re.compile('@DATA')
	@staticmethod
	def header_version_parser(match):
		try:
			version_tuple = tuple([ int(d) for d in match.group('header_version').split('.') ])
			return version_tuple
		except:
			return None
	@staticmethod
	def sniff_version(parseme, max_lines = 30, start_line = 0):
		"""
		Returns a tuple like ('File format', Format version(), Number of header lines)
		"""
		#line_number=0
		next_section=ARFF_header.relation_section_regex.match
		for line_number, line in enumerate(parseme, start=start_line+1):
			if line_number > max_lines:
				return None, None, line_number
			n=next_section(line)
			if n:
				break
			# else:
			m = ARFF_header.header_format_regex.match(line)
			if m:
				format = m.group('header_format')
				continue
			m = ARFF_header.header_version_regex.match(line)
			if m:
				version = ARFF_header.header_version_parser(m)
				continue
			m = ARFF_header.comment_regex.match(line)
			if m and m.group('comment'):
				print line_number, line
		return format, version, line_number
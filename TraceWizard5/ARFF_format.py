import re

class ARFF_format:
	comment_regex=re.compile('%\s*(?P<comment>.*)')
	#
	attribute_section_regex=re.compile('@RELATION\s+(?P<relation_name>.*)\s*', re.IGNORECASE)
	attribute_regex=re.compile('@ATTRIBUTE\s+(?P<attribute_name>\w+)\s+(?P<attribute_parameters>.*)\s*', re.IGNORECASE)
	data_section_regex=re.compile('@DATA', re.IGNORECASE)
class ARFF_format_with_version(ARFF_format):
	header_format_regex=re.compile('%\s*Format:\s*(?P<header_format>.*)')
	header_version_regex=re.compile('%\s?Version:\s*(?P<header_version>.*)')
	#
	@staticmethod
	def header_version_parser(match):
		try:
			version_tuple = tuple(int(d) for d in match.group('header_version').split('.'))
			return version_tuple
		except:
			return None
	@staticmethod
	def sniff_version(parseme, max_lines = 30, start_line = 1):
		"""
		Returns a tuple like ('File format', Format version(), Number of header lines)
		"""
		next_section=ARFF_format.attribute_section_regex.match
		for line_number, line in enumerate(parseme, start=start_line):
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
				version = ARFF_format_with_version.header_version_parser(m)
				continue
			m = ARFF_format.comment_regex.match(line)
			if m and m.group('comment'):
				print line_number, line
		return format, version, line_number
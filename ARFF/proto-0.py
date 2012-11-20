#! env python
import os.path
import re

"""
This stub reads TraceWizard 5 v 5.1.0.30 format files. Fitting it for other
versions will come later.
"""

header_format_regex=re.compile('%\s*Format:\s*(?P<header_format>.*)')
header_version_regex=re.compile('%\s?Version:\s*(?P<header_version>.*)')
def header_version_parser(match):
	try:
		version_tuple = tuple([ int(d) for d in match.group('header_version').split('.') ])
		return version_tuple
	except:
		return None
comment_regex=re.compile('%(?P<comment>.*)')
#
relation_section_regex=re.compile('@RELATION\s+(?P<relation_name>.*)')
relation_regex=re.compile('@ATTRIBUTE\s+(?P<attribute_name>\w+)\s+(?P<attribute_parameters>.*)')
#
fixture_profile_section_regex=re.compile('% @FIXTURE PROFILES')
fixture_profile_header_regex=re.compile('% FixtureClass,MinVolume,MaxVolume,MinPeak,MaxPeak,MinDuration,MaxDuration,MinMode,MaxMode')
# right now, each fixture profile is simply a comment
log_attribute_section_regex=re.compile('% @LOG')
log_attribute_regex=re.compile('%\s+(?P<attribute_name>\w+)\s*[,]\s*(?P<attribute_value>.*)')
# right now, each logged attribute is simply a comment
data_section_regex=re.compile('@DATA')
flow_section_regex=re.compile('% @FLOW')

def sniff_version(parseme, max_lines = 30):
	"""
	Returns a tuple like ('File format', 'Format version', Number of header lines)
	"""
	line_number=0
	next_section=relation_section_regex.match
	for line in parseme:
		if line_number > max_lines:
			return None, None, line_number
		line_number += 1
		n=next_section(line)
		if n:
			break
		# else:
		m = header_format_regex.match(line)
		if m:
			format = m.group('header_format')
			continue
		m = header_version_regex.match(line)
		if m:
			version = header_version_parser(m)
			continue
		m = comment_regex.match(line)
		if m and m.group('comment'):
			print line_number, line
	return format, version, line_number
#
def parse_header(parseme):
	format, version, line_number = sniff_version(parseme)
	print format, version, line_number, "lines"
	#
	# Fix here to add other formats:
	assert format == 'Trace Wizard Analysis'
	assert version == (5,1,0,30)
	#
	next_section=fixture_profile_section_regex.match
	attributes = []
	for line in parseme:
		line_number += 1
		n=next_section(line)
		if n:
			break
		# else:
		m = relation_regex.match(line)
		if m:
			attributes.append( (m.group('attribute_name'), m.group('attribute_parameters')) )
	print "Attributes:"
	for n, l in enumerate(attributes):
		print '\t', n, l
	#
	next_section=log_attribute_section_regex.match
	print line_number, line
	fixture_profiles = []
	for line in parseme:
		line_number += 1
		n=next_section(line)
		if n:
			break
		# else:
		m = comment_regex.match(line) # TODO
		if m:
			fixture_profiles.append(m.groupdict())
	print "Fixtures:", fixture_profiles
	#
	next_section=data_section_regex.match
	log_attributes = {}
	for line in parseme:
		line_number += 1
		n=next_section(line)
		if n:
			break
		# else:
		m = log_attribute_regex.match(line)
		if m:
			log_attributes[m.group('attribute_name')] = m.group('attribute_value')
	print "Log attributes:", log_attributes
	return line_number
#
def parse_TraceWizard5_ARFF(parseme):
	line_number = parse_header(parseme)
	# pick up from the data section
	next_section=flow_section_regex.match
	events=[]
	for line in parseme:
		line_number += 1
		n = next_section(line)
		if n:
			break
		# else:
		events.append(line)
	print len(events), "events"
	# last section
	next_section = None
	flows = []
	for line in parseme:
		line_number += 1
		m = comment_regex.match(line)
		if m:
			flows.append(line)
	print len(flows), "flow data points"
if __name__ == '__main__':
	desktop=os.path.expandvars('%UserProfile%\Desktop')
	testfn=os.path.join(desktop, '12S704.twdb')
	#with open(testfn) as fi:
	#	wholefile=fi.read()
	#parseme = wholefile.split()
	with open(testfn) as parseme:
		parse_TraceWizard5_ARFF(parseme)
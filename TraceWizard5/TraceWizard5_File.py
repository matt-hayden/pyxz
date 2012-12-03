#! env python
from collections import namedtuple
from datetime import datetime, timedelta

from TraceWizard4.MeterMaster_Common import Interval, ratedata_t
from TraceWizard5_parser import TraceWizard5_parser

Interval = namedtuple('Interval', 'min max')
"""
These subclasses define the different TraceWizard5 file formats. There are at
least 4.
"""
class TraceWizard5000_parser(TraceWizard5_parser):
	minimum_version = (5,1,0,0)
	number_of_event_fields = 11
	has_fixture_profile_section=False
	has_log_attribute_section=False
	#	
	flows_header = 'EventID', 'DateTimeStamp', 'Duration', 'RateData'
	#
	def _get_body_formatters(self):
		formatters = TraceWizard5_parser._get_body_formatters(self) # yuck
		formatters[0] = int
		formatters[1] = lambda s: datetime.strptime(s, self.event_timestamp_format)
		formatters[2] = formatters[1]
		formatters[3] = lambda t: timedelta(seconds=float(t))
		return formatters
class TraceWizard5100_parser(TraceWizard5000_parser):
	minimum_version = (5,1,0,0)
	number_of_event_fields = 12
	#
class TraceWizard51021_parser(TraceWizard5100_parser):
	"""
	The minor version is likely wrong here.
	"""
	minimum_version = (5,1,0,9)
	number_of_event_fields = 15
	has_fixture_profile_section=True
	#
	check_fixture_profile_header = True
	fixture_profile_header = ['FixtureClass', 'MinVolume', 'MaxVolume', 'MinPeak', 'MaxPeak', 'MinDuration','MaxDuration', 'MinMode', 'MaxMode']
	Fixture_Profile = namedtuple('Fixture_Profile', 'FixtureClass Volume Peak Duration Mode')
	def parse_fixture_profile_line(self, line, row_factory = None):
		row_factory = row_factory or self.Fixture_Profile
		#
		fa = line.split(',')
		fv = [ ratedata_t(v or 0) for v in fa[1:] ]
		fp = [fa[0],]+[ Interval(x,y) for x,y in zip(fv[0::2], fv[1::2]) ]
		return row_factory(*fp)
	#
class TraceWizard51030_parser(TraceWizard51021_parser):
	"""
	The minor version is likely wrong here.
	"""
	minimum_version = (5,1,0,30)
	has_log_attribute_section=True
#
TraceWizard5_classes = [ TraceWizard51030_parser, TraceWizard51021_parser, TraceWizard5100_parser, TraceWizard5000_parser ]
def TraceWizard5_File(filename,
					  load = True,
					  sniffer = None
					  ):
	"""
	Convenience function to return the correct parser for an ARFF file.
	"""
	if not sniffer:
		sniffer = TraceWizard5_parser.sniff_version
	with open(filename) as fi:
		format, version, line_number = sniffer(fi)
	for vclass in TraceWizard5_classes:
		if version >= vclass.minimum_version:
			break
	return vclass(filename, load = load)
if __name__ == '__main__':
	import logging
	import os.path
	#
	logging.basicConfig(level=logging.DEBUG)
	#
	#desktop=os.path.expandvars('%UserProfile%\Desktop')
	tempdir=os.path.expandvars('%TEMP%\example-traces')
	example_traces = ['01_07nov2011_16nov2011.twdb',
					  '09_22oct2011_append_21dec2011.twdb',
					  '12S704.twdb'
					  ]
	fn = os.path.join(tempdir, example_traces[-1])
	# Example 1: read a whole file:
	t = TraceWizard5_File(fn)
	# Example 2: read only the header:
	#t = TraceWizard5_File(fn, load=False)
	#t.parse_ARFF_header()
	
	print "t =", t
	t.print_long_summary()
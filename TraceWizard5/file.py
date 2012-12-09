#! env python
from collections import namedtuple
from datetime import datetime, timedelta
from logging import debug, info, warning, error, critical

from TraceWizard4 import Interval, ratedata_t
from TraceWizard5_parser import TraceWizard5_parser

"""
These subclasses define the different TraceWizard5 file formats. There are at
least 4.
"""
class TraceWizard5000_parser(TraceWizard5_parser):
	minimum_version = (5,0,0,0)
	#format = "%s %s" % (__package__, ".".join(str(i) for i in minimum_version))
	number_of_event_fields = 11
	has_fixture_profile_section=False
	has_log_attribute_section=False
	#
	storage_interval = timedelta(seconds = 10)
	#
	flows_header = 'EventID', 'DateTimeStamp', 'Duration', 'RateData'
	#
	def define_log_attributes(self, pairs):
		TraceWizard5_parser.define_log_attributes(self, pairs) # yuck
		#
		try:
			fn = os.path.split(self.path)[-1]
			n = os.path.splitext(fn)[0]
		except Exception as e:
			debug("Error finding label for %s: %s" %(self.path, e))
			n = "<%s>" % self.__class__.__name__
		self.label = n
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
	#format = "%s %s" % (__package__, ".".join(str(i) for i in minimum_version))
	number_of_event_fields = 12
	#
class TraceWizard51021_parser(TraceWizard5100_parser):
	"""
	The minor version is likely wrong here.
	"""
	#format = "TraceWizard5 5.1.0.21"
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
	#format = "TraceWizard5 5.1.0.30"
	minimum_version = (5,1,0,30)
	#format = "%s %s" % (__package__, ".".join(str(i) for i in minimum_version))
	has_log_attribute_section=True
	#
	def define_log_attributes(self, pairs):
		TraceWizard5_parser.define_log_attributes(self, pairs) # yuck
		#
		n = self.log_attributes['CustomerID']
		if not n:
			try:
				fn = os.path.split(self.path)[-1]
				n = os.path.splitext(fn)[0]
				if not n:
					# LogFileName found only in later versions of TW5
					fn = os.path.split(self.log_attributes['LogFileName'])[-1]
					n = "(from %s)" % fn
			except:
				n = "<%s>" % self.__class__.__name__
		self.label = n
	#
#
TraceWizard5_classes = [ TraceWizard51030_parser, TraceWizard51021_parser, TraceWizard5100_parser, TraceWizard5000_parser ]
def TraceWizard5_File(filename, *args, **kwargs):
	"""
	Convenience function to return the correct parser for an ARFF file.
	"""
	sniffer = kwargs.pop('sniffer', TraceWizard5_parser.sniff_version)
	with open(filename) as fi:
		format, version, line_number = sniffer(fi)
	for vclass in TraceWizard5_classes:
		if version >= vclass.minimum_version:
			break
	return vclass(filename, *args, **kwargs)
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
	fn = os.path.join(tempdir, '12S704.twdb')
	# Example 1: read a whole file:
	t = TraceWizard5_File(fn)
	# Example 2: read only the header:
	#t = TraceWizard5_File(fn, load=False)
	#t.parse_ARFF_header()
	
	print fn, "(found)" if os.path.exists(fn) else "(not found)"
	print "t =", t
	t.print_summary()
	#for d, es in t.get_events_by_day():
	#	print d, sum([e.Volume for e in es])
	for e, fs in t.get_events_and_flows():
		print "Event:", e
		print "Flows:", fs
		break
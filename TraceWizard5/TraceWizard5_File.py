#! env python
from datetime import datetime, timedelta

from TraceWizard5_parser import TraceWizard5_parser

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
	def parse_event_line(self, line, volume_t=float, ratedata_t=float, row_factory=None):
		row_factory = row_factory or self.EventRow
		return row_factory(
			int(line[0]),
			datetime.strptime(line[1], self.event_timestamp_format),
			datetime.strptime(line[2], self.event_timestamp_format),
			timedelta(seconds=float(line[3])),
			bool(line[4]),
			bool(line[5]),
			line[6],
			volume_t(line[7]),
			ratedata_t(line[8]),
			ratedata_t(line[9]),
			line[10]
			)
class TraceWizard5100_parser(TraceWizard5000_parser):
	minimum_version = (5,1,0,0)
	number_of_event_fields = 12
	#
	def parse_event_line(self, line, volume_t=float, ratedata_t=float, row_factory=None):
		row_factory = row_factory or self.EventRow
		return row_factory(
			int(line[0]),
			datetime.strptime(line[1], self.event_timestamp_format),
			datetime.strptime(line[2], self.event_timestamp_format),
			timedelta(seconds=float(line[3])),
			bool(line[4]),
			bool(line[5]),
			line[6],
			volume_t(line[7]),
			ratedata_t(line[8]),
			ratedata_t(line[9]),
			line[10].strip(),
			line[11]
			)
				
class TraceWizard51021_parser(TraceWizard5100_parser):
	"""
	The minor version is likely wrong here.
	"""
	minimum_version = (5,1,0,9)
	number_of_event_fields = 15
	has_fixture_profile_section=True
	#
	def parse_event_line(self, line, volume_t=float, ratedata_t=float, row_factory=None):
		row_factory = row_factory or self.EventRow
		return row_factory(
			int(line[0]),
			datetime.strptime(line[1], self.event_timestamp_format),
			datetime.strptime(line[2], self.event_timestamp_format),
			timedelta(seconds=float(line[3])),
			bool(line[4]),
			bool(line[5]),
			line[6],
			volume_t(line[7]),
			ratedata_t(line[8]),
			ratedata_t(line[9]),
			line[10].strip(),
			line[11],
			bool(line[12]),
			bool(line[13]),
			bool(line[14])
			)
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
					  sniffer=TraceWizard5_parser.sniff_version):
	"""
	Convenience function to return the correct parser for an ARFF file.
	"""
	with open(filename) as fi:
		format, version, line_number = sniffer(fi)
		t = None
		for vclass in TraceWizard5_classes:
			if version >= vclass.minimum_version:
				break
	return vclass(filename, load = load)
if __name__ == '__main__':
	import os.path
	#desktop=os.path.expandvars('%UserProfile%\Desktop')
	tempdir=os.path.expandvars('%TEMP%\example-traces')
	example_traces = ['01_07nov2011_16nov2011.twdb',
					  '09_22oct2011_append_21dec2011.twdb',
					  '12S704.twdb'
					  ]
	fn = os.path.join(tempdir, example_traces[-1])
	t = TraceWizard5_File(fn)
	t.print_summary()
	for d, ef in t.get_events_by_day():
		daily_total = sum(e.Volume for (e, f) in ef)
		print d, " = ", daily_total, t.events_units
	
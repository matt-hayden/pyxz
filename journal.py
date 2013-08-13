#!env python
from collections import namedtuple
import os
import os.path

import dateutil.parser

def round_timedelta(td, **kwargs):
	denom = timedelta(**kwargs).total_seconds()
	num = td.total_seconds()
	return timedelta(seconds=denom*round(num/denom))

class TimeLogEntry(object):
	@staticmethod
	def time_parser(*args, **kwargs):
		return dateutil.parser.parse(*args, **kwargs)
	
	def __init__(self, *data, **kwargs):
		self.begin, self.end, self.desc = None, None, ''
		if data: self.from_row(data)
	def from_row(self, row):
		if row[0]:
			if isinstance(row[0], basestring):
				self.begin = self.time_parser(row[0])
			else:
				self.begin = row[0]
		if row[1]:
			if isinstance(row[1], basestring):
				self.end = self.time_parser(row[1])
			else:
				self.end = row[1]
		self.desc = row[2]
	@property
	def dur(self):
		try:	return self.end-self.begin
		except:	return None
	def to_tuple(self):
		return self.begin, self.end, self.desc
	def __nonzero__(self):
		return any(self.to_tuple())
	def __repr__(self):
		return "{0}('{1.begin}','{1.end}','{1.desc}')".format(self.__class__.__name__, self)

def parse_timelog(rows, lastrow = []):
	def chrono_key(row):
		return row[0] or row[1]
	#
#	last = TimeLogEntry()
	rows.sort(key=chrono_key)
	entries = [ TimeLogEntry(*row) for row in rows ]
	nentries = len(entries)
	if entries:
		for n, entry in enumerate(entries):
			if not entry.begin:
				try: entry.begin = entries[n-1].end
				except: pass
			if not entry.end:
				try: entry.end = entries[n+1].begin
				except: pass
			yield entry
		if lastrow: yield lastrow
	else: print "No input"
	
#
fields = 'begin end desc'.split()
#
if __name__ == '__main__':
	from datetime import datetime, timedelta
	from itertools import groupby
	
	import pytz
	
	import local.stat
	
	filename = os.environ.get('JOURNAL_FILE', os.path.expanduser('~/.journal'))
	sep = os.environ.get('JOURNAL_SEP', '\t')
	default_timezone = pytz.timezone(os.environ.get('TZ','America/Denver'))
	#
	stat = local.stat.stat(filename)
	last_modify = stat.st_mtime.replace(tzinfo=default_timezone)
	now = datetime.now().replace(tzinfo=default_timezone)
	with open(filename, 'Ur') as fi:
		rows = [ line.strip('\n').split(sep, len(fields)-1) for line in fi]
	for day, entries in groupby(parse_timelog(rows, lastrow=TimeLogEntry(last_modify, now, "<placeholder>")), key=lambda e: e.begin.date()):
		print day
		for entry in entries:
			try: mydur = round_timedelta(entry.dur, minutes=15)
			except: mydur = ""
			try: myend = "{:%H:%M}".format(entry.end)
			except: myend = "\t"
			print "{0.begin:%H:%M}-{1}\t{2}\t{0.desc}".format(entry, myend, mydur)
		print
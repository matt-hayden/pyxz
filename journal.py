#!env python
from collections import namedtuple
import os
import os.path

import dateutil.parser

class TimeLogEntry(object):
	@staticmethod
	def time_parser(*args, **kwargs):
		return dateutil.parser.parse(*args, **kwargs)
	
	def __init__(self, *data, **kwargs):
		self.begin, self.end, self.desc = None, None, ''
		if data: self.from_row(data)
	def from_row(self, row):
		if row[0]: self.begin = self.time_parser(row[0])
		if row[1]: self.end = self.time_parser(row[1])
		self.desc = row[2]
	@property
	def duration(self):
		try:	return self.end-self.begin
		except:	return None
	def to_tuple(self):
		return self.begin, self.end, self.desc
	def __nonzero__(self):
		return any(self.to_tuple())
	def __repr__(self):
		return "{0}('{1.begin}','{1.end}','{1.desc}')".format(self.__class__.__name__, self)

def parse_timelog(rows):
	def chrono_key(row):
		return row[0] or row[1]
	#
	last = TimeLogEntry()
	rows.sort(key=chrono_key)
	for row in rows:
		this = TimeLogEntry(*row)
		if not this.begin: this.begin = last.end
		yield this
		last = this
	else: print "No input"
#
fields = 'begin end desc'.split()
#
if __name__ == '__main__':
	from datetime import datetime, timedelta
	
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
		rows = [ line.rstrip().split(sep, len(fields)-1) for line in fi]
	print rows
	journal = list(parse_timelog(rows))
	if not journal[-1].end:
		if last_modify - journal[-1].begin < timedelta(minutes=5):
			journal[-1].end = now
		else:
			journal[-1].end = last_modify
	print journal
#!env python
from collections import namedtuple
from datetime import datetime, timedelta
from itertools import groupby
import os
import os.path

import dateutil.parser

import local.stat

def round_timedelta(td, **kwargs):
	denom = timedelta(**kwargs).total_seconds()
	num = td.total_seconds()
	return timedelta(seconds=denom*round(num/denom))

class JournalError(Exception):
	pass
class TimeLogEntry(object):
	"""
	A (simple?) representation of a timestamped log entry. .begin and .end
	define a duration .dur. 
	"""
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
				if self.begin:
					default = self.begin.replace(minute=0, second=0, microsecond=0)
					self.end = self.time_parser(row[1], default=default)
				else:
					self.end = self.time_parser(row[1])
			else:
				self.end = row[1]
		self.desc = row[2]
	def append(self, text):
		sep = '\n' if (self.desc[-1] in ' \t\n') else ' '
		if isinstance(text, basestring):
			self.desc += sep+text.strip()
		else:
			self.desc += sep.join(text)
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

def parse_timelog(rows, lastrow=[], is_sorted=True):
	if not is_sorted: # multi-line is not allowed
		def chrono_key(row):
			return row[0] or row[1]
		rows.sort(key=chrono_key)
		entries = [ TimeLogEntry(*row) for row in rows ]
	else: # allow multi-line entries where no begin or end is specified
		entries = []
		for row in rows:
			if entries:
				if not row[0] and not row[1]:
					entries[-1].append(text=row[-1])
				else:
					try:
						default = entries[-1].end.replace(minute=0, second=0, microsecond=0)
						entries.append(TimeLogEntry(*row, default=default))
					except:
						entries.append(TimeLogEntry(*row))
			else:
				entries.append(TimeLogEntry(*row))
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
	else: raise JournalError("No input")
#
fields = 'begin end desc'.split()

def parse_file(filename, sep, default_timezone):
	stat = local.stat.stat(filename)
	last_modify = stat.st_mtime.replace(tzinfo=default_timezone)
	now = datetime.now().replace(tzinfo=default_timezone)
	if  timedelta(minutes=5) < now - last_modify:
		lastrow = TimeLogEntry(last_modify, now, "<placeholder>")
	else: lastrow = []
	with open(filename, 'Ur') as fi:
		rows = [ line.strip('\n').split(sep, len(fields)-1) for line in fi]
		multiline = any(not row[0] and not row[1] for row in rows)
	return parse_timelog(rows, lastrow=lastrow, is_sorted=multiline)
def print_timelog(*args, **kwargs):
	for day, entries in groupby(parse_file(*args, **kwargs), key=lambda e: e.begin.date()):
		print day
		for entry in entries:
			try: mydur = round_timedelta(entry.dur, minutes=15)
			except: mydur = ""
			try: myend = "{:%H:%M}".format(entry.end)
			except: myend = "\t"
			print "{0.begin:%H:%M}-{1}\t{2}\t{0.desc}".format(entry, myend, mydur)
		print
#
if __name__ == '__main__':	
	import pytz
	
	filename = os.environ.get('JOURNAL_FILE', os.path.expanduser('~/.journal'))
	if os.path.isdir(filename): filename=os.path.join(filename, 'current')
	sep = os.environ.get('JOURNAL_SEP', '\t')
	default_timezone = pytz.timezone(os.environ.get('TZ','America/Denver'))
	#
	print_timelog(filename=filename, sep=sep, default_timezone=default_timezone)

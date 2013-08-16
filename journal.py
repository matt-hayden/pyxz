#!env python
from collections import namedtuple
from datetime import datetime, timedelta
from itertools import groupby
import os
import os.path
import string

import dateutil.parser

import local.stat
from local.xdatetime import round_timedelta

class JournalError(Exception):
	pass
class TimeLogEntry(object):
	"""
	A (simple?) representation of a timestamped log entry. .begin and .end
	define a duration .dur. 
	"""
	@staticmethod
	def time_parser(*args, **kwargs):
		"""
		Subclasses can change the method for parsing datetime from text.
		"""
		return dateutil.parser.parse(*args, **kwargs)
	
	def __init__(self, *data, **kwargs):
		self.begin, self.end, self.desc = None, None, ''
		if data: self.from_row(data)
	def from_row(self, row):
		if row[0]:
			if isinstance(row[0], basestring):
				self.begin = self.time_parser(row[0])
			else: # assume datetime
				self.begin = row[0]
		if row[1]:
			if isinstance(row[1], basestring):
				if self.begin:
					default = self.begin.replace(minute=0, second=0, microsecond=0)
					self.end = self.time_parser(row[1], default=default)
				else:
					self.end = self.time_parser(row[1])
			else: # assume datetime
				self.end = row[1]
		self.desc = row[2]
	def append(self, text):
		"""
		Add extra text to the end of the description.
		"""
		sep = '\n' if (self.desc[-1] in string.whitespace) else ' '
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
	def __iadd__(self, other):
		assert not self.end
		assert not other.begin
		self.end = other.end
		self.append(other.desc)
		return self # important!
#
fields = 'begin end desc'.split()
def parse_timelog(rows, is_sorted=True):
	"""
	Input: iterator of 3 text fields: (begin, end, desc)
	Output: iterator of TimeLogEntry objects
	
	If begin is empty, end is copied from the previous row. If end is empty,
	begin is copied from the next row. If this row has no begin, and the
	previous row has no end, then they're combined.	If both are empty, then
	that row is assumed to be a continuation of the previous line.
	
	Arguments:
	If is_sorted=False, then multi-line continuation is disabled and rows is
	sorted by begin or end timestamp.
	"""
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
				try:
					if entries[n-1].end:
						entry.begin = entries[n-1].end
					else: # combine the last with this
						entries[n-1] += entry
						entries.pop(n)
				except Exception as e: print e
			if not entry.end:
				try: entry.end = entries[n+1].begin
				except Exception as e: print e
		return entries
	else: raise JournalError("No input")
def parse_file(filename, sep, default_timezone):
	"""
	Input: filename
	Output: iterator of TimeLogEntry objects
	
	Expects a text file formatted with exactly two separators. parse_timelog()
	takes (begin, end, desc) from each line. 
	"""
	stat = local.stat.stat(filename)
	last_modify = stat.st_mtime.replace(tzinfo=default_timezone)
	now = datetime.now().replace(tzinfo=default_timezone)
	with open(filename, 'Ur') as fi:
		rows = [ line.strip('\n').split(sep, len(fields)-1) for line in fi]
		multiline = any(not row[0] and not row[1] for row in rows)
	if timedelta(minutes=5) < now - last_modify:
		lastrow = TimeLogEntry(last_modify, now, "<placeholder>")
		return parse_timelog(rows, is_sorted=multiline)+[lastrow]
	else:
		return parse_timelog(rows, is_sorted=multiline)
def print_timelog(*args, **kwargs):
	"""
	See parse_file() for arguments
	"""
	def key(e):
		try: return e.begin.date() or e.end.date()
		except:
			print e
			return None
	for day, entries in groupby(parse_file(*args, **kwargs), key=key):
		print day
		for entry in entries:
			try: mydur = round_timedelta(entry.dur, minutes=15)
			except: mydur = ""
			try: mybegin = "{:%H:%M}".format(entry.begin)
			except: mybegin = "\t"
			try: myend = "{:%H:%M}".format(entry.end)
			except: myend = "\t"
			try:
				print "{1}-{2}\t{3}\t{0.desc}".format(entry, mybegin, myend, mydur)
			except:
				print "Bad form:", entry
		print
#
if __name__ == '__main__':	
	import pytz
	
	filename = os.environ.get('JOURNAL_FILE', os.path.expanduser('~/.journal'))
	if os.path.isdir(filename): filename=os.path.join(filename, 'current')
	sep = os.environ.get('JOURNAL_SEP', '|')
	default_timezone = pytz.timezone(os.environ.get('TZ','America/Denver'))
	#
	print_timelog(filename=filename, sep=sep, default_timezone=default_timezone)

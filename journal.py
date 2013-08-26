#!env python
from collections import namedtuple
from datetime import datetime, timedelta
from itertools import groupby
import string

import dateutil.parser

import local.xstat
import local.flatten

from local.xdatetime import round_timedelta
from local.console.size import to_columns

def pretty_duration(dur, roundto=15, threshold=timedelta(minutes=5)):
	if not isinstance(dur, timedelta):
		dur = timedelta(seconds=dur)
	if dur < timedelta(minutes=5):
		dur = timedelta(minutes=roundto)
	if roundto:
		dur = round_timedelta(dur, minutes=roundto)
	minutes, seconds = divmod(dur.total_seconds(), 60)
	hours, minutes = divmod(minutes, 60)
	return "{:4.0f}:{:02.0f}".format(hours, minutes)
#	return str(dur).rsplit(':',1)[0]

class JournalError(Exception):
	pass
SplitTimeLogEntry = namedtuple('SplitTimeLogEntry', 'begin end dur desc')
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
	def split(self, seps=[',', ' + '], label='split'):
		"""
		Return the entry divided equally if a separator is present in the
		description.
		"""
		for sep in seps:
			if sep in self.desc: break
		else: return [self]
		parts = [ s.strip() for s in self.desc.split(sep) if s.strip() ]
		if label:
			parts = [ "{} ({}:{})".format(s, label, n) for n, s in enumerate(parts, start=1)]
		divided_dur = self.dur/len(parts)
		return [ SplitTimeLogEntry(self.begin, self.end, divided_dur, part) for part in parts ]
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
def parse_timelog(rows, is_sorted=True, split_on_commas=True):
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
					entries[-1].append(text=row[-1]) # this means: modify the last entry, note the keyword arg
				else:
					try:
						default = entries[-1].end.replace(minute=0, second=0, microsecond=0)
						entries.append(TimeLogEntry(*row, default=default))
					except:
						entries.append(TimeLogEntry(*row))
			else:
				entries.append(TimeLogEntry(*row))
	if entries:
		drop_by_index = []
		for n, this in enumerate(entries):
			if not this.begin:
				try:
					if entries[n-1].end:
						this.begin = entries[n-1].end
					else: # combine the this into last
						entries[n-1] += this
						this.append("(combined with above)")
						drop_by_index.append(n)
						continue
				except Exception as e: print "entry", n, e
			if not this.end:
				try:
					if entries[n+1].begin: this.end = entries[n+1].begin
				except Exception as e: print "entry", n, e
		if drop_by_index:
			drop_by_index.sort(reverse=True)
			dropped = [entries.pop(i) for i in drop_by_index]
	#
	if split_on_commas:
		split_entries = []
		for e in entries:
			split_entries.extend(e.split())
		return split_entries
	else:
		return entries

def parse_file(filename,
			   sep,
			   default_timezone,
			   placeholder='<placeholder>',
			   threshold=timedelta(minutes=15)):
	"""
	Input: filename
	Output: iterator of TimeLogEntry objects
	
	Expects a text file formatted with exactly two separators. parse_timelog()
	takes (begin, end, desc) from each line. Empty lines are skipped.
	"""
	mystat = local.xstat.stat(filename)
	last_modify = mystat.st_mtime.replace(tzinfo=default_timezone)
	now = datetime.now().replace(tzinfo=default_timezone)
	with open(filename, 'Ur') as fi:
		lines = [ line.strip('\n') for line in fi ]
	rows = [ line.split(sep, len(fields)-1) for line in lines if line]
	multiline = any(not row[0] and not row[1] for row in rows)
	if placeholder and (threshold < now - last_modify):
		tail = TimeLogEntry(last_modify, now, placeholder)
		return parse_timelog(rows, is_sorted=multiline)+[tail]
	else:
		return parse_timelog(rows, is_sorted=multiline)

def print_TimeLogEntry(tle):
	try: mydur = pretty_duration(tle.dur)
	except: mydur = "\t"
	try: mybegin = "{:%H:%M}".format(tle.begin)
	except: mybegin = " "*6
	try: myend = "{:%H:%M}".format(tle.end)
	except: myend = " "*6
	try:
		return "{}-{}{:>6} {}".format(mybegin, myend, mydur, tle.desc[:79].replace('\n',' '))
	except:
		return "Bad form:", tle

def print_timelog(*args, **kwargs):
	"""
	See parse_file() for arguments
	"""
	def key1(entry):
		try: return entry.begin.isocalendar()[:-1]
		except Exception as e:
			print e, entry
	def key2(entry):
		try: return entry.begin.date() or entry.end.date()
		except Exception as e:
			print e, entry
	for yearweek, g1 in groupby(parse_file(*args, **kwargs), key=key1):
		week_string = "{} wk {}".format(*yearweek)
		print "****** "+week_string+" ******"
		weekly_total = timedelta()
		for day, g2 in groupby(g1, key=key2):
			day_string = "{:%b-%d}".format(day)
			entries = list(g2)
			daily_total = sum((e.dur for e in entries if e.dur), timedelta())
			weekly_total += daily_total
			print "*** "+day_string+" ***"
			for entry in entries: print print_TimeLogEntry(entry)
			## remember the padding, changing the 7-sizes below to 9
#			print to_columns((print_TimeLogEntry(entry) for entry in entries), sep=" || ", pad="  ")
			print "{:<11}{:>7}".format('='+day_string+'=', pretty_duration(daily_total))
			print
		print "{:<11}{:>7}".format(week_string, pretty_duration(weekly_total))
		print
#
if __name__ == '__main__':
	import os
	import os.path
	
	import pytz

	filename = os.environ.get('JOURNAL_FILE', os.path.expanduser('~/.journal'))
	if os.path.isdir(filename): filename=os.path.join(filename, 'current')
	sep = os.environ.get('JOURNAL_SEP', '|')
	default_timezone = pytz.timezone(os.environ.get('TZ','America/Denver'))
	#
#	for line in parse_file(filename=filename, sep=sep, default_timezone=default_timezone):
#		print line
	print_timelog(filename=filename, sep=sep, default_timezone=default_timezone)

#!env python
from collections import Counter
from datetime import timedelta
from itertools import groupby
import shlex

from local.xdatetime import mul_timedelta

import journal

def tokenize(text,
			 sep='_',
			 proper_patterns = ['Abu Dhabi', 'San '],
			 stopwords='in out start started done',
			 shell_comments=True):
	pr = [ (p, p.replace(' ',sep)) for p in proper_patterns ]
	if isinstance(stopwords, basestring): stopwords = stopwords.split()
#	stopwords = [ s.title() for s in stopwords ]
#	text = text.title()
	for ppat, repl in pr:
		if ppat in text: text = text.replace(ppat, repl)
	return [ s for s in shlex.split(text, comments=shell_comments) if s not in stopwords ]

def get_keywords(entries,
				 divisor=None,
				 placeholder='<placeholder>',
				 threshold=0.15):
	"""
	"""
	daily_total = sum((e.dur for e in entries if e.dur), timedelta())
	time_by_keyword = Counter([])
	total_time_seconds = daily_total.total_seconds()
	portion_multiplier = 1/total_time_seconds
	
	for entry in entries:
		text = entry.desc
		keywords = tokenize(text) or [placeholder]
		for keyword in keywords:
			try: sec = entry.dur.total_seconds()
			except: sec = 0
			time_by_keyword[keyword] += sec
	items = time_by_keyword.items()
	items.sort(reverse=True, key=lambda p: p[-1])
	keywords = [ (k, journal.pretty_duration(sec).strip(), sec*portion_multiplier) for (k, sec) in items]
	if placeholder:
		daily_rep = sum(portion for keyword, dur, portion in keywords)
		deficit = 1-daily_rep
		if threshold < deficit < 1:
			keywords.append((placeholder, mul_timedelta(deficit, daily_total), deficit))
	return keywords
def aggregate_by_week(entries):
	"""
	See parse_file() for arguments
	"""
	def key1(e):
		try: return e.begin.isocalendar()[:-1]
		except Exception as e:
			print e, entry
	def key2(entry):
		try: return entry.begin.date() or entry.end.date()
		except Exception as e:
			print e, entry
	for yearweek, g1 in groupby(entries, key=key1): # over weeks
		try:
			week_string = "{} wk {}".format(*yearweek)
		except:
			print "Skipping {}".format(list(g1))
			continue
		print "****** "+week_string+" ******"
		weekly_total = timedelta()
		for day, g2 in groupby(g1, key=key2): # over days
			day_string = "{:%b-%d}".format(day)
			print "*** "+day_string+" ***"
			entries = list(g2)
			daily_total = sum((e.dur for e in entries if e.dur), timedelta())
			weekly_total += daily_total
			for entry in entries: print journal.print_TimeLogEntry(entry)
			print "{:=>18} {}".format(journal.pretty_duration(daily_total), "Total")
			print
			keywords = get_keywords(entries)
			for keyword, dur, portion in keywords:
				print "{:<30}{}".format(keyword, dur)
			daily_rep = sum(portion for keyword, dur, portion in keywords)
			if not (0.95 < daily_rep < 1.05):
				print "{:-<29} {:>3.0%}".format("Representing", daily_rep)
			print
if __name__ == '__main__':	
	import os
	import os.path
	
	import pytz

	filename = os.environ.get('JOURNAL_FILE', os.path.expanduser('~/.journal'))
	if os.path.isdir(filename): filename=os.path.join(filename, 'current')
	sep = os.environ.get('JOURNAL_SEP', '|')
	default_timezone = pytz.timezone(os.environ.get('TZ','America/Denver'))
	entries = journal.parse_file(filename=filename, sep=sep, default_timezone=default_timezone)
	aggregate_by_week(entries)
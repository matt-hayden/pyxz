#!env python
from collections import Counter
from datetime import timedelta
import shlex

import journal

def get_keywords(entries, stopwords='in out start started done'):
	"""
	"""
	if isinstance(stopwords, basestring): stopwords = stopwords.split()
	stopwords = [ s.title() for s in stopwords ]
	time_by_keyword = Counter([])
	total_time_seconds = sum(entry.dur.total_seconds() for entry in entries if entry.dur)
	portion_multiplier = 1/total_time_seconds
	for entry in entries:
		for keyword in [s.title() for s in shlex.split(entry.desc)]:
			if keyword not in stopwords:
				try: sec = entry.dur.total_seconds()
				except: sec = 0
				time_by_keyword[keyword] += sec
	items = time_by_keyword.items()
	items.sort(reverse=True, key=lambda p: p[-1])
	return [ (k, journal.pretty_duration(sec), sec*portion_multiplier) for (k, sec) in items]

if __name__ == '__main__':	
	import os
	import os.path
	
	import pytz

	filename = os.environ.get('JOURNAL_FILE', os.path.expanduser('~/.journal'))
	if os.path.isdir(filename): filename=os.path.join(filename, 'current')
	sep = os.environ.get('JOURNAL_SEP', '|')
	default_timezone = pytz.timezone(os.environ.get('TZ','America/Denver'))
	entries = journal.parse_file(filename=filename, sep=sep, default_timezone=default_timezone)
	print entries
	print get_keywords(entries)
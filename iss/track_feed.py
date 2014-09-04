from . import *

def parse_value(feeddict):
	items = Namespace()
	text = feeddict['summary_detail']['value']
	lines = re.split('\\s*<br[ /]*>\\s*', text)
	for lineno, line in enumerate(lines):
		if line:
			name, value = re.split('\\s*:\\s*', line, 1)
			if 'DATE' in name.upper():
				try:
					date = dateutil.parser.parse(value)
					value = date
				except:	pass
			elif 'TIME' in name.upper() and 'Date' in items:
				try:
					timestamp = dateutil.parser.parse(value, default=items['Date'])
					value = timestamp
				except:	pass
			items[name] = value
	return items

def _get_sightings(url=sighting_feed_url):
	feed = feedparser.parse(url)
#	sightings = [ parse_value(e) for e in feed.entries ]
#
	for e in feed.entries:
		yield parse_value(e)
def get_sightings(*args, **kwargs):
	sightings = [ (e.pop('Time'), e) for e in _get_sightings(*args) ]
	sightings.sort()
	return sightings

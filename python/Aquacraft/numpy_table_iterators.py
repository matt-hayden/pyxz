#!env python
from collections import defaultdict
from datetime import datetime
from itertools import groupby

indoor_outdoor_by_fixture = defaultdict(lambda:'')
indoor_outdoor_by_fixture.update( (k, 'Indoor') for k in ['Bathtub', 'Clothes washer', 'Dishwasher', 'Faucet', 'Leak', 'Shower', 'Toilet'])
indoor_outdoor_by_fixture.update( (k, 'Outdoor') for k in ['Irrigation', 'Pool'])

def sumas_lookup(text):
	"""
	Some @ events mistakenly made it into the database
	"""
	if not text:
		return ''
	if text.startswith('Clotheswashe'):
		return 'Clothes washer'
	if text.endswith('@'):
		return sumas_lookup(text.replace('@','').strip())
	return text
def indooroutdoor_key(row):
	return indoor_outdoor_by_fixture[sumas_lookup(row[1])]
def groupby2(table, key, presorted=True):
	if not presorted:
		try:
			table.sort(key=key)
		except:
			table = sorted(table, key=key)
	for group, rows in groupby(table, key=key):
		yield group, rows
def events_by_keycode(table, **kwargs):
	def key(row):
		return row[0]
	for keycode, rows in groupby2(table, key=key, **kwargs):
		yield keycode, rows
def events_by_day(table, **kwargs):
	def key(row):
		return row[3].astype(datetime).date()
	for day, eg1 in groupby2(table, key=key, **kwargs):
		yield day, eg1
def indooroutdoor_by_day(table, **kwargs):
	for day, eg1 in events_by_day(table):
		events = sorted(eg1, key=indooroutdoor_key, **kwargs)
		yield (day, [(category, list(eg2)) for category, eg2 in groupby(events, key=indooroutdoor_key) if category])
def events_by_hod(table, **kwargs):
	def key(row):
		return row[3].astype(datetime).hour
	for hod, eg1 in groupby2(table, key=key, **kwargs):
		yield hod, eg1
def events_by_fixture(table, **kwargs):
	hfc = kwargs.pop('honor_first_cycles', False)
	def key(row):
		return sumas_lookup(row[1])
	for name, eg3 in groupby2(table, key=key, **kwargs):
		yield name, eg3
#
#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Open a series of traces and output the following tables:
Main fixture table:
				Start	End		nDays	Day1	...	Day14
Keycode Fixture
00X000	Bathtub	M-D-Y	M-D-Y	14		0.0			0.0

Hot fixture table: (same format as above)

Indoor total, similar format
"""
#import logging
#logging.basicConfig(level = logging.DEBUG if __debug__ else logging.WARNING)

from collections import defaultdict
import csv
from itertools import groupby
import os.path
import sys

from Aquacraft.keycodes import splitext, AquacraftMultiKeycode
from TraceWizard5 import TraceWizard5_import

truncate_partial_days = True # False for testing against TraceWizard
fixture_lookup = { 'Bathtub':			('Bathtub',			'Indoor'),
				   'Clotheswasher':		('Clothes washer',	'Indoor'),
				   'Clothes washer':	('Clothes washer',	'Indoor'),
				   'Cooler':			('Cooler',			'Indoor'),
				   'Dishwasher':		('Dishwasher',		'Indoor'),
				   'Faucet':			('Faucet',			'Indoor'),
				   'Humidifier':		('Humidifier',		'Indoor'),
				   'Irrigation':		('Irrigation',		'Outdoor'),
				   'Leak':				('Leak',			'Outdoor' or 'Leak'),
				   'Other':				('Other',			'Indoor'),
				   'Shower':			('Shower',			'Indoor'),
				   'Toilet':			('Toilet',			'Indoor'),
				   'Treatment':			('Treatment',		'Indoor'),
				   'Duplicate':			('Duplicate',		''),
				   'Noise':				('Noise',			''),
				   'Unclassified':		('Other',			'Indoor'),
				 }
input_fixture_names = set(fixture_lookup.keys())
output_fixture_names = set(n for n, c in fixture_lookup.values() if c)

def fixture_key(event):
	return event.Class
def fixture_sort(fixture):
	n, c = fixture_lookup[fixture]
	return c, n

def get_event_totals_by_day(filename, unit_conversion=1.0, stderr=sys.stderr):
	trace = TraceWizard5_import(filename)
	dirname, basename = os.path.split(filename)
	keycode, ext = splitext(basename)
	ndays = (trace.ends - trace.begins).days
	volume_by_day = { f: [0]*(ndays+2) for f in output_fixture_names }
	for day, eventsg in trace.get_events_by_day(logical=truncate_partial_days):
		dayi = (day-trace.begins.date()).days # begins is part of the truncated period before the first whole day
		events = sorted(eventsg, key=fixture_key)
		for fixture, eventsg in groupby(events, key=fixture_key):
			try:
				fixture, category = fixture_lookup[fixture]
			except KeyError:
				raise NotImplementedError("'{}' is missing from fixture_lookup".format(fixture))
			if category:
				volume_by_day[fixture][dayi] = sum(e.Volume for e in eventsg)
			else: print >>stderr, fixture, "ignored"
	for f, ar in sorted(volume_by_day.items(), key=lambda r: fixture_sort(r[0])):
		yield [keycode, trace.begins, trace.ends, f]+(ar[1:-2] if truncate_partial_days else ar)
	yield [keycode, trace.begins, trace.ends, 'Indoor total']+[unit_conversion*sum(s) for s in zip(*volume_by_day.values())]
def main(filenames, header=None, stderr=sys.stderr):
	trace_files_by_suffix = defaultdict(list)
	if header is None:
		if truncate_partial_days:
			header = ['Keycode', 'Begins after', 'Ends before', 'Fixture']+['Day_{:02d}'.format(i) for i in range(1,15)]
		else:
			header = ['Keycode', 'Begins after', 'Ends before', 'Fixture']+['Day_{:02d}'.format(i) for i in range(16)]
	#
	for pathname in filenames:
		if not os.path.exists(pathname):
			print >>stderr, pathname, "ignored"
			continue
		dirname, basename = os.path.split(pathname)
		keycode, ext = splitext(basename)
		if ext.upper() in ('.TWDB'):
			sgroup = keycode.decode_suffix() # returns a tuple now
			trace_files_by_suffix[sgroup].append(pathname)
	for suffix, trace_files in trace_files_by_suffix.iteritems():
		group_label = ' '.join(suffix) if suffix else 'main'
		summary_table_filename = group_label+'_fixture_use_by_days.csv'
		with open(summary_table_filename, 'wb') as fo:
			writer = csv.writer(fo)
			if fo.tell() <= 0:	writer.writerow(header)
			for fn in trace_files:
				print "Processing", fn
				try:
					rows = list(get_event_totals_by_day(fn))
					writer.writerows(rows)
					writer.writerow([])
				except Exception as e:
					print >>stderr, fn, "errored:", e
if __name__ == '__main__':
	import glob
	args = sys.argv[1:] or glob('*.twdb')
	main(args)
import logging
import os.path

from collections import defaultdict	
from datetime import datetime, date, time, timedelta
from itertools import groupby

from decimal import Decimal
import numpy

from TraceWizard5.TraceWizard5_File import TraceWizard5_File

#
logging.basicConfig(level=logging.DEBUG)

fixture_type_lookup = {'Toilet': 'Indoor', 'Dishwasher': 'Indoor', 'Cooler': 'Outdoor', 'Clotheswasher': 'Indoor', 'Faucet': 'Indoor', 'Shower': 'Indoor', 'Other': 'Indoor', 'Irrigation': 'Outdoor', 'Treatment': 'Indoor', 'Leak': 'Leak', 'Bathtub': 'Indoor'}

#
#desktop=os.path.expandvars('%UserProfile%\Desktop')
tempdir=os.path.expandvars('%TEMP%\example-traces')
fn = os.path.join(tempdir, '12S704.twdb')
# Example 1: read a whole file:
t = TraceWizard5_File(fn)
# Example 2: read only the header:
#t = TraceWizard5_File(fn, load=False)
#t.parse_ARFF_header()

print "t =", t
t.print_summary()

def get_logical_events(t, logical=True, timespan=None, midnight = time()):
	if timespan:
		begin_date, end_date = timespan
	else:
		begin_date, end_date = t.begins.date(), t.ends.date()
		if (t.begins.hour > 6):
			begin_date += timedelta(days=1)
		if (t.ends.hour > 21):
			end_date += timedelta(days=1)
	# convert to datetime rather than date objects:
	if type(begin_date) == date:
		begin_date = datetime.combine(begin_date, midnight)
	if type(end_date) == date:
		end_date = datetime.combine(end_date, midnight)
	for e, fs in t.get_events_and_flows():
		if (begin_date <= e.StartTime <= end_date):
			yield e, fs
#
event_count_by_fixture = defaultdict(int)
volume_by_fixture = defaultdict(float) # Decimal)
for e in t.events:
	event_count_by_fixture[e.Class] += 1
	volume_by_fixture[e.Class] += e.Volume # Decimal(e.Volume)
print "Counts:", event_count_by_fixture
print "Volume:", volume_by_fixture
#
if False:
	l=list(get_logical_events(t))
	total_by_day = [ (d, sum(e.Volume for e, fs in efs)) for d, efs in groupby(l, lambda x: x[0].StartTime.date()) ]
	total_volume = sum(e for d, e in total_by_day)
	for d, v in total_by_day:
		print d, v
	days = (t.ends - t.begins).days
	print days
if True:
	days = (t.ends - t.begins).days
	ftypes = set(fixture_type_lookup.values())
	hour_by_fixture = { k:numpy.zeros((days+1, 24)) for k in fixture_type_lookup.keys() }
	hour_by_type = { ft:numpy.zeros((days+1, 24)) for ft in ftypes }
	hour_matrix = numpy.zeros((days+1, 24))
	#
	hour_keyer = lambda ef: ef[0].StartTime.hour
	fixture_keyer = lambda ef: ef[0].Class # depends on TW implementation, yuck
	#
	for d, efs in t.get_events_by_day():
		dn = (d-t.begins.date()).days 
		for h, hefs in groupby(efs, hour_keyer):
			hl = sorted(list(hefs), key = fixture_keyer)
			daily_total = 0
			for fixture_name, hefs in groupby(hl, key = fixture_keyer):
				ftype = fixture_type_lookup[fixture_name]
				s = sum(e.Volume for (e, fs) in hefs)
				daily_total += s
				hour_by_fixture[fixture_name][dn][h] = s
			hour_matrix[dn][h] = daily_total
	for fixture_name in hour_by_fixture.keys():
		ftype = fixture_type_lookup[fixture_name]
		hour_by_type[ftype] += hour_by_fixture[fixture_name]
	# hour_matrix/hour_matrix.sum()
	#
	print "All hours:", hour_by_fixture['Leak']
	print "HOD:", hour_by_fixture['Leak'].sum(axis=0)
	print "Total:",  hour_by_fixture['Leak'].sum()
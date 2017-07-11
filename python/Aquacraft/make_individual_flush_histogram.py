#! env python
"""
Input: none
Output: a frequency count of Toilet events

Many parameters may be changed to make this more generally useful
"""

from collections import defaultdict
import csv
from itertools import groupby
from math import fsum
import os.path

from numpy import arange, dot, histogram

from odbc_export_table import connect, get_connection_string, get_table

curdir = "Z:\\Projects\\+REUWS_2\\Task8_Log_Data_and_Analysis"
main_tables = [ _.strip() for _ in open('main_tables.list','Ur') ]
labeled_files = [ (_.split('\\')[0], os.path.join(curdir, _)) for _ in main_tables ]

fixture = 'Toilet'

"Bins are explicitly set here and separated by a minimum distance of"
"10^-(decimal_places)"
decimal_places = 2
"""Toilet histogram bins taken from Denver. Note that numpy.histogram does not
include events higher than the largest edge, whereas Excel's frequencies()
function emits an extra last value for +more."""
volume_bins = arange(0, 7+0.5, 0.25)
volume_bins[-1] = 50

event_sql = '''SELECT StartTime, Duration, Peak, Volume, Mode
FROM exportNormalizedTraces INNER JOIN tblFixtureLookup ON tblFixtureLookup.[_LocalFixtureNameID] = exportNormalizedTraces.FixtureNameID
where tblFixtureLookup.CountAs = ?
order by Volume;'''

### this expression doesn't work:
#event_sql = '''
#SELECT TimeValue([StartTime]) AS ToD, exportNormalizedTraces.Duration, exportNormalizedTraces.Peak, #exportNormalizedTraces.Volume, exportNormalizedTraces.Mode
#FROM exportNormalizedTraces INNER JOIN  tblFixtureLookup ON tblFixtureLookup.[_LocalFixtureNameID] = #exportNormalizedTraces.FixtureNameID
#WHERE (((tblFixtureLookup.CountAs) In ("Toilet")));
#'''
### the where clause causes an error

frequency_by_bin = defaultdict(int)

total_from_summaries = 0
for label, fn in labeled_files:
	print "Processing", label+":"
	print "\t", fn
	#
	connection_string = get_connection_string(fn, read_only=True)
	connection = connect(connection_string)
	#
	this_freq_total = 0.0
	this_vol_total = 0.0
	table = get_table(sql=event_sql, parameters=fixture, connection=connection)
	for bin, eg in groupby(table, 
							   lambda _:round(_.Volume,decimal_places)
							   ):
		events = list(eg)
		f, v = len(events), fsum(_.Volume for _ in events)
		frequency_by_bin[bin] += f
		this_freq_total += bin*f
		this_vol_total += v
	print "\t", "File histogram total:", this_freq_total
	#
	table = get_table(sql='''select sum([{} Total Gal]) from tblSummary;'''.format(fixture),
					  connection=connection)
	assert len(table) == 1
	summary_total = table[0][0]
	total_from_summaries += summary_total
	print "\t", "Summary total:", summary_total
	print "\t", "Differance (due to rounding):", summary_total - this_freq_total, "({} before rounding)".format(this_vol_total - this_freq_total)
#
with open('{}_frequencies.csv'.format(fixture), 'wb') as fo:
	writer = csv.writer(fo)
	writer.writerow(['Event volume bin', 'Frequency'])
	writer.writerows(sorted(frequency_by_bin.items()))

measurements, counts = frequency_by_bin.keys(), frequency_by_bin.values()
values_total = dot(measurements,counts)

print
print "Overall:"
print "\t", sum(counts), "total", fixture, "events"
print "\t", len(counts), "unique measures at", decimal_places, "decimal precision"
print "\t", "Histogram total:", values_total
print "\t", "Summary total:", total_from_summaries
print "\t", "Differance (due to rounding):", total_from_summaries - values_total

freq, fbins = histogram(measurements, bins=volume_bins, weights=counts)
with open('{}_histogram.csv'.format(fixture), 'wb') as fo:
	writer = csv.writer(fo)
	writer.writerow(['Lower edge of bin', 'Upper edge of bin', 'Frequency'])
	writer.writerows(zip(fbins[:-1], fbins[1:], freq))

#!env python
from collections import Counter
import cPickle as pickle

import numpy as np
import pandas as pd

names = ['ID', 'Timestamp', 'IntervalLength', 'PulseCount']
NutationRate = 0.01388888

filename = r'Z:\Projects\Abu Dhabi\Monitoring Period 1\renamed\7596S011A.TXT' # dots
#filename = r'Z:\Projects\Abu Dhabi\Monitoring Period 1\renamed-date-slashes\7596S013A.TXT' # slashes

table = pd.read_csv(filename, header=None, names=names, index_col=[1], parse_dates=[1], dayfirst=True)

begins, ends = table.index[0], table.index[-1]

ID_frequencies = Counter(table['ID'])
if len(ID_frequencies) == 1:
	table.ID, n = ID_frequencies.popitem()
	del table['ID'] # can be undone by table['ID'] = ID
else:
	print filename, "has {} different IDs:".format(len(ID_frequencies))
	for p, freq in ID_frequencies.most_common():
		print "{:>6}{:>10}".format(p, freq)
IntervalLength_frequencies = Counter(table['IntervalLength'])
if len(IntervalLength_frequencies) == 1:
	IntervalLength, n = IntervalLength_frequencies.popitem()
	di = pd.DatetimeIndex(start=begins, end=ends, freq=str(IntervalLength)+'S')
	del table['IntervalLength'] # can be undone by table['IntervalLength'] = IntervalLength
else:
	print filename, "has {} different interval length:".format(len(IntervalLength_frequencies))
	for i, freq in IntervalLength_frequencies.most_common():
		print "{:>6}{:>10}".format(i, freq)
raw_frequencies = Counter(table['PulseCount'])
if raw_frequencies.most_common(1)[0][0] == 0: # valid zeros make up most of the observations
	zero_mask = (table['PulseCount']==0)
	compressed = table[~zero_mask]
	compressed['FlowRate'] = NutationRate*compressed['PulseCount']/(IntervalLength/60.0)
	print "table is represented in {:,} bytes".format(len(pickle.dumps(table)))
	print "compressed is represented in {:,} bytes".format(len(pickle.dumps(compressed)))

	# eval() these
	canned_locals = {'begins':begins, 'ends':ends, 'IntervalLength':IntervalLength}
	index_string = """pd.DatetimeIndex(start='{0[begins]}', end='{0[ends]}', freq=({0[IntervalLength]}, 'S'))""".format(canned_locals)
	table_string = """compressed.reindex(di, fill_value=0)"""
	print "table can be resurrected by:"
	print """di = eval({})""".format(index_string)
	print """table = compressed.reindex(di, fill_value=0)"""
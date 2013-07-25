#!env python
import logging
logging.basicConfig(level=logging.DEBUG)

from collections import defaultdict
from datetime import datetime
import os
import os.path
import cPickle as pickle

import handles
from local.walk import separate_paths_at_component

db_filename = os.path.expanduser('~/.whats_open.pickle')
db_filename = '.whats_open.pickle'
handle_executable=r'C:\Program Files\SysinternalsSuite\handle.exe'

path_term = 'Aquacraft'

if os.path.exists(db_filename):
	with open(db_filename) as fi:
		history = pickle.load(fi)
	last_timestamp = max(history)
	last_entries = history[last_timestamp]
else:
#	history = defaultdict(set)
	history = {}
	last_entries = None
now = datetime.now()
historykey = now

#print history

shs = handles.handle_search([path_term], handle_executable=handle_executable)

pp = set()
for p in separate_paths_at_component((x.path for x in shs), path_term):
	pp.add((p[-1], os.path.join(p) ))
#

if last_entries:
	new_entries = pp - last_entries
	if new_entries:
		history[historykey] = new_entries
else:
	history[historykey] = pp

#print history

with open(db_filename, 'wb') as fo:
	pickle.dump(history, fo)
print "New files detected since {} ({}):".format(last_timestamp, now-last_timestamp)
for basename, path in history.get(historykey, []):
	print basename, path
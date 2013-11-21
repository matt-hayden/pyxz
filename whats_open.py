#!env python
import logging
logging.basicConfig(level=logging.DEBUG)

from collections import defaultdict
from datetime import datetime
from itertools import groupby
import os
import os.path
import cPickle as pickle
import sys

import handles
from local.walk import separate_paths_at_component

db_filename = os.path.expanduser('~/.whats_open.pickle')
db_filename = '.whats_open.pickle'

path_term = 'Aquacraft'
ignore_paths = set([('\\Device\\Mup\\;Z:00000000000f64c6\\aquacraft_nas', 'Aquacraft')])

def main(historykey=None):
	now = datetime.now()
	historykey = historykey or now
	if sys.stdin.isatty():
		handle_executable=r'C:\Program Files\SysinternalsSuite\handle.exe'
		matching_handles = handles.handle_search([path_term], handle_executable=handle_executable)
	else:
		"""
		Redirect the output of Sysinternals' handle.exe to this script
		"""
		lines = sys.stdin.readlines()
		matching_handles = handles.parse_sysinternals_handle(lines)
	open_paths = separate_paths_at_component((x.path for x in matching_handles), path_term)
	if ignore_paths:
		open_paths -= ignore_paths
	"""
	Load the cache of previously-seen paths
	"""
	if os.path.exists(db_filename):
		with open(db_filename) as fi:
			history = pickle.load(fi)
		last_timestamp = max(history)
		last_entries = history[last_timestamp]
	else:
		history = {}
		last_entries = set()	
	#
	if open_paths == last_entries:
		print "No changes made to {}:".format(db_filename)
		for splitpath in open_paths:
			print os.path.join(*(splitpath[1:] or splitpath))
	else:
		history[historykey] = open_paths
		# save the cache back
		with open(db_filename, 'wb') as fo:
			pickle.dump(history, fo)
if __name__ == '__main__':
	from datetime import timedelta
	
	from local.xsched import enter_repeat, scheduler
	
	delay = period = timedelta(minutes=15)
	try:
		main()
	except Exception as e:
		print >> sys.stderr, "Not running: {}".format(e)
	else:
		print "Running every {}".format(period)
		enter_repeat(delay, 1, main, (), period=period)
		scheduler.run()
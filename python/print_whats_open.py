#! /usr/bin/env python3
from datetime import datetime, timedelta
import os
import cPickle as pickle
import sys

def compact_whats_open(filename, begins=None, ends=None):
	ends = ends or datetime.now()
	begins = begins or (ends-timedelta(days=15))
	if os.path.exists(filename):
		with open(filename) as fi: history = pickle.load(fi)
		newhistory = {k:v for k,v in history.iteritems() if begins <= k <= ends}
		os.rename(filename, filename+'.bak')
		with open(filename, 'wb') as fo: pickle.dump(newhistory, fo)
def print_whats_open(filename):
	if os.path.exists(filename):
		with open(filename) as fi: history = pickle.load(fi)
		historykeys = sorted(history.keys(), reverse=True)
		latest_timestamp, previous_timestamp = historykeys[:2]
		latest_files = history[latest_timestamp]
		previous_files = history[previous_timestamp]
		removed_entries = previous_files - latest_files
		if removed_entries:
			print "Files closed after {}:".format(latest_timestamp)
			for splitpath in removed_entries:
				print os.path.join(*(splitpath[1:] or splitpath)), "in", splitpath[0]
		#
		new_entries = latest_files - previous_files
		if new_entries:
			if history:
				print "New files detected since {}:".format(latest_timestamp)
			else:
				print "New history file {} started".format(db_filename)
			for splitpath in new_entries:
				print os.path.join(*(splitpath[1:] or splitpath)), "in", splitpath[0]
	else:
		print >> sys.sterr, "{} doesn't exist".format(filename)
if __name__ == '__main__':
	import sys
	from whats_open import db_filename
	args = sys.argv[1:]
	if args:
		print_whats_open(args[0])
	else:
		print_whats_open(db_filename)

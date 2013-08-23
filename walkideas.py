#!env python
import os
import os.path
import sys

def commonsuffix(args, splitext=None):
	if splitext: # check for extensions...
		for c in range(3):
			args = [os.path.splitext(arg)[0] for arg in args]
	rev = [ s[::-1] for s in args ]
	revprefix = os.path.commonprefix(rev)
	if revprefix: return revprefix[::-1]
	elif splitext: return ''
	elif splitext is None: return commonsuffix(args, splitext=True)	# Try again without filename extension
	else: return ''
def commonnames_by_pattern(filenames):
	"""
	GENERATOR
	"""
	prefix = os.path.commonprefix(fn.lower() for fn in filenames)
	if prefix:
		while prefix[-1].isdigit(): prefix = prefix[:-1]
		if prefix:
			prefix_chars = len(prefix)
			filenames = [ fn[prefix_chars:] for fn in filenames ]
	suffix = commonsuffix(filenames)
	if suffix:
		suffix_chars = len(suffix)
		for fn in filenames:
			oddparts = fn.split(suffix)
			yield prefix, oddparts[0], suffix, oddparts[1]
	else:
		for fn in filenames:
			yield prefix, fn

args = sys.argv[1:] or ['.']

for root in args:
	for root, dirs, files in os.walk(root):
		for nameparts in commonnames_by_pattern(files):
			print root, nameparts
else:
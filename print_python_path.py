#! /usr/bin/env python2
from collections import Counter
import os.path
import sys

mc = Counter()
for n,m in sys.modules.iteritems():
	try:
		dirname, basename = os.path.split(m.__file__)
		mc[dirname.upper()] += 1
	except AttributeError: pass

parts = []
for n, p in enumerate(sys.path):
	if os.path.exists(p):
		flag = '*' if os.path.isfile(p) else ' '
	else:
		flag = 'X'
	if sys.prefix in p:
		dp = p.replace(sys.prefix, '${prefix}', 1)
	else:
		dp = p
	parts.append((p, dp, flag, mc[p.upper()], n))

cw = max(len(_[1]) for _ in parts)
print "prefix='{}'".format(sys.prefix)
for path, display, flag, count, order in parts:
	print flag, display.ljust(cw), count or ''

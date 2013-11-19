#!env python
"""
Find the root of a filesystem on UNIX or a drive letter in Windows
"""

import os
import os.path

import sys
args = sys.argv[1:]

prefix = os.path.commonprefix(args)
if isdir(prefix): parent = prefix
else: parent, _ = os.path.split(prefix)
lastparent = ''
stat = os.stat(parent)
laststat = stat

samedev

while samedev and (parent != lastparent):
	parent, lastparent = os.path.dirname(parent), parent
	stat, laststat = os.stat(parent), stat
	samedev = (stat.st_dev == laststat.st_dev)
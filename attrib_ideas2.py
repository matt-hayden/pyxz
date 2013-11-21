#!env python

import os
import os.path

default_extension = '.attrib'
default_subdir = '.attrib'

def guess_attrib(path, expand_search=True):
	if isdir(path): parent = path
	else:
		dirname, basename = os.path.split(path)
		parent = dirname
	if expand_search:
		lastparent = ''
		laststat = None
		while parent != lastparent:
			this_dir = os.path.join(parent, default_subdir)
			if os.path.exists(this_dir):
				attrib_dir = this_dir
				break
			lastparent, parent = parent, os.path.dirname(parent)
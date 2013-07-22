#!env python
from collections import Counter, defaultdict
from logging import debug, info, warning, error, critical
import os
import os.path
import re
import subprocess
import sys

from logging import debug, info, warning, error, critical
import os.path
import sys

from local.flatten import flatten
#from local.xglob import glob
from local.md5sum import md5summer
from local.walk import *

from local.xmimetypes import types_map

from msys_path import *

"""

"""
ignore_types = [ 'application/x-javascript', 'application/x-sh', 'application/x-python-code',
				 'text/plain', 'text/html', 'text/xml', 'text/css', 'text/x-python',
				 '.log' ]
"""
A listing of files and their sizes is kept in tab-separated format. This format
can be generated without Python:
	find -type f -printf '%P\t%s\n' > .sizes
"""
size_db_filename = '.sizes'

def rebase_sizes_files(root, path_filter=(os.path.normpath if sys.platform.startswith('win') else lambda _:_)):
	"""
	GENERATOR
	Re-create a list of <path>\t<bytes>\n for '.sizes' files 
	
	Some platform path issues can be avoided by manipulating paths:
	path_filter=os.path.normpath on Windows, for instance.
	"""
	for sf in find_repositories(root, stopfiles=[size_db_filename]):
		reporoot = os.path.dirname(sf)
		total_size = 0
		debug("Opening {}".format(sf))
		with open(sf) as fi:
			for line in fi:
				try:
					fn, st = line.rstrip().split('\t')
					s = int(st)
					total_size += s
					yield os.path.join(reporoot, path_filter(fn)), s
				except Exception as e:
					critical("Parsing error in {}:{}".format(fi.name, e))
		info("{} total bytes represented in {}".format(total_size, reporoot))
def get_files_by_type_and_size(roots,
							   ignore_types=[],
							   check_if_exist=(sys.platform.startswith('win'))):
	files_by_type_and_size = defaultdict(list)
	unknown_exts_seen = []
	for root in roots:
		for full_path, size in rebase_sizes_files(root):
			dirname, basename = os.path.split(full_path)
			if basename.endswith('~'):
				file_part, ext = os.path.splitext(basename[:-1])
			else:
				file_part, ext = os.path.splitext(basename)
			ext = ext.lower()
			if ext in ['.bak', '.bkp', '.delme', '.old', '.orig']:
				file_part, ext = os.path.splitext(file_part)
				ext = ext.lower()
			try:
				file_type = types_map[ext]
			except:
				if ext not in unknown_exts_seen:
					info("File type unknown for '{}'".format(ext))
					unknown_exts_seen.append(ext)
				file_type = ext
			if file_type in ignore_types:
				continue
			### Windows:
			if check_if_exist:
				full_path = windows_path_from_msys(full_path)
				if not os.path.exists(full_path):
					full_path = full_path.decode('utf_8')
				if not os.path.exists(full_path):
					critical("{} doesn't exist".format(full_path))
			###
			files_by_type_and_size[(file_type, size)].append(full_path)
	return files_by_type_and_size
def get_size_by_type(roots=[],
					 files_by_type_and_size=[],
					 key=None):
	assert roots or files_by_type_and_size
	files_by_type_and_size = files_by_type_and_size or get_files_by_type_and_size(roots, ignore_types=ignore_types)
	if not key:
		def key(mimetype):
			if mimetype.startswith('application'):
				return mimetype
			else:
				try:
					return mimetype.split('/', 1)[0]
				except:
					return mimetype
	print
	total_size = sum(len(fl)*s for (t, s), fl in files_by_type_and_size.iteritems())
	size_by_type = Counter()
	for (t, s), fl in files_by_type_and_size.iteritems():
		size_by_type[key(t)] += s*len(fl)
	total_size = float(sum(size_by_type.values()))
	v = sorted(size_by_type.items(), key=lambda _:_[-1], reverse=True)
	width = max(len(str(_[0])) for _ in v)+1
	print "{:<{width}}{:^13}{:^5}".format("Type", "MB", "%", width=width)
	for t, s in v:
		print "{:_<{width}}{:_>13.0f}{:_>5.0%}".format(t, s/1E6, s/total_size, width=width)
	print "{:<{width}}{:>13.0f}".format("Total", total_size/1E6, width=width)
	return size_by_type
def get_files_of_same_size(roots=[],
						   files_by_type_and_size=[],
						   minsize=0):
	assert roots or files_by_type_and_size
	files_by_type_and_size = files_by_type_and_size or get_files_by_type_and_size(roots, ignore_types=ignore_types)
	files_of_same_size = [ fl for (t, s), fl in files_by_type_and_size.iteritems() if (len(fl) > 1) and (s >= minsize) ]
	debug("Detected {:,} sets of the same size and type:".format(len(files_of_same_size)))
	return files_of_same_size
#
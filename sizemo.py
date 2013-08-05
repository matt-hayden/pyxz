#!env python
"""Find likely-duplicate files as fast as Python is able.

A listing of files and their sizes is kept in tab-separated format. This format
can be generated without Python:
	find -type f -printf '%P\\t%s\\n' > .sizes
"""
if __debug__:
	import logging
	logging.basicConfig(level=logging.DEBUG)

from collections import Counter, defaultdict
from logging import debug, info, warning, error, critical
import os
import os.path
import re
#import subprocess
import sys

import psutil
from subprocess import PIPE

from local.flatten import flatten
#from local.xglob import glob
import local.md5sum as md5sum
from local.units import human_readable_bytes
from local.walk import *
from local.xmimetypes import types_map

from msys_path import *

path_filter=(os.path.normpath if sys.platform.startswith('win') else None)
size_db_filename = '.sizes'

def mksizes(root,
			outfile='',
			overwrite=True,
			find_executable=r'f:\cygwin\bin\find.exe'):
	if not outfile: outfile = os.path.join(root, size_db_filename)
	if not overwrite and os.path.exists(outfile): raise IOError("Refusing to overwrite "+outfile)
	find_args = ['-type', 'f', '-fprintf', outfile, '"%P\t%s\n"']
	debug("Running {}".format([find_executable]+findargs))
	find_process = psutil.Popen([find_executable]+findargs,
								stdout=PIPE, stderr=PIPE, cwd=root)
	stdoutdata, stderrdata = find_process.communicate()
	for line in stdoutdata.splitlines(): warning(line)
	for line in stderrdata.splitlines(): error(line)
	returncode = find_process.wait()
	if returncode:
		error(find_executable+" exited {}".format(returncode))
	else:
		debug(find_executable+" exited {}".format(returncode))
def rebase_sizes_files(root, path_filter=path_filter):
	"""
	GENERATOR
	Re-create a list of <path>\\t<bytes>\\n for '.sizes' files found under root. 
	
	Some platform path issues can be avoided by manipulating paths:
	path_filter=os.path.normpath on Windows, for instance.
	"""
	for sf in find_repositories(root, stopfiles=[size_db_filename]):
		reporoot = os.path.dirname(sf)
		total_size = 0
		if os.path.isfile(sf) and os.path.getsize(sf) == 0:
			error("{} empty".format(sf))
			continue
		else:
			debug("Opening {}".format(sf))
		with open(sf) as fi:
			for line in fi:
				try:
					fn, st = line.rstrip().split('\t')
					s = int(st)
					total_size += s
					if path_filter:
						yield os.path.join(reporoot, path_filter(fn)), s
					else:
						yield os.path.join(reporoot, fn), s
				except Exception as e:
					critical("Parsing error in {}:{}".format(fi.name, e))
		printable_total_size = "{0:3.1f} {1}".format(*human_readable_bytes(total_size))
		info("Total {} = {} B represented in {}".format(printable_total_size, total_size, reporoot))
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
	"""
	Print a table of the space used by different data types.
	"""
	assert roots or files_by_type_and_size
	files_by_type_and_size = files_by_type_and_size or get_files_by_type_and_size(roots, ignore_types=ignore_types)
	if not key:
		def key(mimetype):
			if mimetype.startswith('application'): return mimetype
			else:
				try:	return mimetype.split('/', 1)[0]
				except:	return mimetype
	print
	total_size = sum(len(fs)*s for (t, s), fs in files_by_type_and_size.iteritems())
	size_by_type = Counter()
	for (t, s), fs in files_by_type_and_size.iteritems():
		size_by_type[key(t)] += s*len(fs)
	total_size = float(sum(size_by_type.values()))
	v = sorted(size_by_type.items(), key=lambda _:_[-1], reverse=True)
	width = max(len(str(_[0])) for _ in v)+1
	print "{:<{width}}{:^13}{:^5}".format("Type", "Size", "%", width=width)
	for t, s in v:
		printable_total_size = "{0:3.1f} {1}".format(*human_readable_bytes(s))
		print "{:_<{width}}{:_>13}{:_>5.0%}".format(t, printable_total_size, s/total_size, width=width)
	printable_total_size = "{0:3.1f} {1}".format(*human_readable_bytes(total_size))
	print "{:<{width}}{:>13}".format("Total", printable_total_size, width=width)
	return size_by_type
def get_files_of_same_size(roots=[],
						   files_by_type_and_size=[],
						   minsize=0):
	assert roots or files_by_type_and_size
	files_by_type_and_size = files_by_type_and_size or get_files_by_type_and_size(roots, ignore_types=ignore_types)
	if minsize:
		return [ fs for (t, s), fs in files_by_type_and_size.iteritems() if (len(fs) > 1) and (s >= minsize) ]
	else:
		return [ fs for (t, s), fs in files_by_type_and_size.iteritems() if (len(fs) > 1) ]
#
def main(roots, ignore_types):
	files_by_type_and_size = get_files_by_type_and_size(roots, ignore_types=ignore_types)
	if not files_by_type_and_size:
		debug("No files found")
		for root in roots: mksizes(root)
	get_size_by_type(files_by_type_and_size=files_by_type_and_size)
	files_of_same_size = get_files_of_same_size(files_by_type_and_size=files_by_type_and_size)
	# UNIX might use os.samefile here
	
	# this could be useful to lookup md5s for files:
	# md5_by_filename = dict(md5sum.md5reader(flatten(files_of_same_size)))
	# but, we want to invert that lookup
	lookup = defaultdict(list)
	print "files_of_same_size:", files_of_same_size
	info("Forming MD5SUM.txt for files that don't have one")
	md5sum.md5maker(flatten(files_of_same_size))
#	for path, params in md5sum.md5reader(flatten(files_of_same_size)):
#		lookup[params].append(path)
#	duplicates = [(fs, params) for params, fs in lookup.iteritems() if len(fs) > 1]
#	if duplicates:
#		print "The following files are probably duplicates:"
#		for (binary, md5), fs in duplicates:
#			print "{:1}{:X}".format("*" if binary else " ", md5), " ".join(fs)
	return 0
if __name__ == '__main__':	
	ignore_types = [ 'application/x-javascript', 'application/x-sh', 'application/x-python-code',
					 'text/plain', 'text/html', 'text/xml', 'text/css', 'text/x-python',
					 '.log' ]
	args = sys.argv[1:] or ['.']
	sys.exit(main(args, ignore_types=ignore_types))
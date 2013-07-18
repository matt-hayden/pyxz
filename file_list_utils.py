#!env python
from collections import Counter, defaultdict
from logging import debug, info, warning, error, critical
import os.path
import sys

from local.xmimetypes import types_map

from msys_path import *

unknown_exts_seen = []
def read_filename_size_list(args, ignore_types=[], check_if_exist=(sys.platform.startswith('win'))):
	files_by_type_and_size = defaultdict(list)
	unknown_exts_seen = []
	#
	for arg in args:
		debug("Reading "+arg)
		with open(arg) as fi:
			linestep = 1
			for linenum, line in enumerate(fi, start=1):
				if not (linenum % linestep):
					debug("{:d} lines read from {}".format(linenum, arg))
					linestep *= 10
				### Only correct for a specific format:
				relative_path, full_path, size = line.strip().split('\t')
				file_part, ext = os.path.splitext(relative_path)
				###
				ext = ext.lower()
				if ext in ['.old', '.orig']:
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
				files_by_type_and_size[(file_type, int(size))].append(full_path)
			debug("{:d} lines read from {}".format(linenum, arg))
	return files_by_type_and_size
#
def grouper(mimetype):
	if mimetype.startswith('application'):
		return mimetype
	else:
		try:
			return mimetype.split('/')[0]
		except:
			return mimetype
def print_totals_by_type(files_by_type_and_size, grouper=grouper):
	print
	total_size = sum(len(fl)*s for (t, s), fl in files_by_type_and_size.iteritems())
	size_by_type = Counter()
	for (t, s), fl in files_by_type_and_size.iteritems():
		size_by_type[grouper(t)] += s*len(fl)
	total_size = float(sum(size_by_type.values()))
	v = sorted(size_by_type.items(), key=lambda _:_[-1], reverse=True)
	width = max(len(str(_[0])) for _ in v)+1
	print "{:<{width}}{:^13}{:^5}".format("Type", "MB", "%", width=width)
	for t, s in v:
		print "{:_<{width}}{:_>13.0f}{:_>5.0%}".format(t, s/1E6, s/total_size, width=width)
	print "{:<{width}}{:>13.0f}".format("Total", total_size/1E6, width=width)
#!env python
"""
Utility for reading md5sum files and generating MD5 values.
"""
from logging import debug, info, warning, error, critical
import os.path
#import subprocess
import sys

import psutil
from subprocess import PIPE

from walk import walklist

if sys.platform.startswith('win'):
	md5sum_filename = 'MD5SUM.txt'
	md5sum_executable = 'md5sum.exe'
else:
	md5sum_filename = 'MD5SUM'
	md5sum_executable = 'md5sum'

_md5sum_file_cache = {}
def _gen_parsed_md5sum(filename):
	debug('Reading '+filename)
	with open(filename, 'Ur') as fi:
		for line in fi:
			line = line.strip()
			hexs, binary, filename = line[:32], line[33] == '*', line[34:]
			yield (filename, (binary, int(hexs, 16)))
def parse_md5sum_file(filename, reload=False):
#	global _md5sum_file_cache
#	if not reload and filename in _md5sum_file_cache:
#		return _md5sum_file_cache[filename]
#	else:
#		contents = dict(_gen_parsed_md5sum(filename))
#		_md5sum_file_cache[filename] = contents
#		return contents
	return dict(_gen_parsed_md5sum(filename))
#def _gen_md5sum_lookup():
#	global _md5sum_file_cache
#	for md5sum_filename, contents in _md5sum_file_cache.iteritems():
#		dirname, basename = os.path.split(md5sum_filename)
#		for filename, params in contents:
#			yield os.path.join(dirname, filename), params
#def load_md5sum_cache():
#	return list(_gen_md5sum_lookup())
#
def md5maker(filenames,
			 md5sum_filename=md5sum_filename,
			 mode='a',
			 skip=False,
			 recurse=False,
			 **kwargs):
	"""
	Generates MD5 checksums recursively. Checksum files are always generated
	local to the input filenames, so multiple checksum files may be generated!
	
	Input: a list of filenames
	Arguments:
		md5sum_filename		The preferrered filename that would be checked against
		mode				'a' for append to md5sum_filename, 'w' to overwrite it
		skip				Should md5 still be calculated if file already exists in md5sum_filename?
	"""
	for root, dirs, files in walklist(filenames):
		if root and not os.path.isdir(root): # 'filenames' is probably stale
			error("Non-existent directory '{}' encountered, ignoring all {} files under it".format(root, len(files)))
			continue
		if dirs:
			if recurse:
				for d in dirs: md5maker(os.listdir(os.path.join(root,d)), recurse=recurse)
			else: warning("non-recursive: directories {} ignored".format(dirs))
		md5sum_file = os.path.join(root, md5sum_filename)
		unanalyzed_files = set(files)
		nf = len(unanalyzed_files)
		#
		if skip and os.path.exists(md5sum_file):
			parsed_md5sum_file = parse_md5sum_file(md5sum_file)
			already_analyzed_files = set(_[0] for _ in parsed_md5sum_file)
			if already_analyzed_files:
				unanalyzed_files -= already_analyzed_files
				info("{} files skipped in {}".format(nf-len(unanalyzed_files), md5sum_file))
		if unanalyzed_files:
#			with open(md5sum_file, mode) as refile:
#				subprocess.check_call([md5sum_executable]+list(unanalyzed_files), stdout=refile, cwd=root)
			debug("Running {}".format([md5sum_executable]+list(unanalyzed_files)))
			md5sum_process = psutil.Popen([md5sum_executable]+list(unanalyzed_files),
										  stdout=PIPE, stderr=PIPE, cwd=root)
			stdoutdata, stderrdata = md5sum_process.communicate()
			with open(md5sum_file, mode) as refile: refile.write(stdoutdata)
			for line in stderrdata.splitlines(): error(line)
			returncode = md5sum_process.wait()
			if returncode:
				error(md5sum_executable+" exited {}".format(returncode))
			else:
				debug(md5sum_executable+" exited {}".format(returncode))
			parse_md5sum_file(md5sum_file, reload=True) # refresh the cache
#def md5reader(filenames):
#	"""
#	In this function, paths are local. This may complicate lists moved from
#	different systems.
#	"""
#	filenames = set(filenames)
#	cache = {path:(binary,md5) for path, (binary, md5) in load_md5sum_cache()}
#	unanalyzed_files = filenames - set(cache)
#	if unanalyzed_files:
#		md5maker(unanalyzed_files) # should refresh the cache
#		del cache
#	cache = dict(load_md5sum_cache())
#	return [(p, cache[p]) for p in filenames]
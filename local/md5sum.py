#!env python
"""
Utility for reading md5sum files and generating MD5 values.
"""
from logging import debug, info, warning, error, critical
import os.path
import subprocess
import sys

from walk import gen_rdf_from_list

if sys.platform.startswith('win'):
	md5sum_filename = 'MD5SUM.txt'
	md5sum_executable = 'md5sum.exe'
else:
	md5sum_filename = 'MD5SUM'
	md5sum_executable = 'md5sum'

md5sum_file_cache = {}
def _gen_parsed_md5sum(filename):
	debug('Reading '+filename)
	with open(filename, 'Ur') as fi:
		for line in fi:
			line = line.strip()
			md5text, binary, filename = line[:32], line[33] == '*', line[34:]
			yield (filename, binary, int(md5text, 16))
def parse_md5sum_file(filename):
	if filename in md5sum_file_cache:
		return md5sum_file_cache[filename]
	else:
		contents = list(_gen_parsed_md5sum(filename))
		md5sum_file_cache[filename] = contents
		return contents
#
def md5summer(filenames,
			  md5sum_filename=md5sum_filename,
			  mode='a',
			  skip=False,
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
	for root, dirs, files in gen_rdf_from_list(filenames):
		if dirs:
			warning("directories {} in argument ignored".format(dirs))
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
			debug("Running {} {}{}{}".format(md5sum_executable, root, os.path.sep, list(unanalyzed_files)))
			with open(md5sum_file, mode) as refile:
				subprocess.check_call([md5sum_executable]+list(unanalyzed_files), stdout=refile, cwd=root)
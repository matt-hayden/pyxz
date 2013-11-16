#! /usr/bin/env python
"""
Walks through a list of PDFs, combining PDFs with similar names. Processed parts
are then collected into a seperate directory.

PDFs are joined using the Java package sejda. Download it from:
	http://www.sejda.org/
"""

from itertools import groupby
from logging import debug, info, warning, error, critical
import os
import os.path
from shutil import move
from subprocess import check_output

# Aquacraft keycode logic is found in a small module:
from keycodes import parse_filename

# sejda is used for PDF processing: (version 1.0.0.M6 is not strictly necessary)
sejda_executable="sejda-console-1.0.0.M6\\bin\\sejda-console.bat"

# Processed output files will be organized by the number of joined parts
output_directories=['', 'joined1', 'joined2', 'joined3', 'joined4']

# Processed input files will end up in move_directory, and can be deleted:
move_directory='_processed'

def combine_similarly_named_files(input_paths, **kwargs):
	"""
	Returns (number of failures, number of files processed)
	"""
	n, nff = 0, 0 # files processed, failed
#	input_paths = [ f for f in input_paths if f ]
	for pn in input_paths:
		if os.path.isdir(pn): raise NotImplementedError("Unable to recurse {}".format(pn))
		elif not os.path.isfile(pn): raise ValueError("{} not found".format(pn))
	n = len(input_paths)
	info("{} input files".format(n))
	input_paths.sort(key=parse_filename)
	for keycode, fi in groupby(input_paths, key=parse_filename):
		filenames = []
		y = filenames.append
		for pn in fi:
			basepart, ext = os.path.splitext(pn)
			if ext.upper() in ('.PDF'):	y(pn)
			else:
				error("{} skipped".format(pn))
				nff+=1
		nf = len(filenames)
		assert nf >= 1, "No PDF files for keycode {}".format(keycode)
		try:
			output_directory=output_directories[nf]
		except:
#			critical("No output directory for {}-size files, {} skipped".format(nf, filenames))
#			continue
			warning("Unexpected {} parts for {}".format(nf, filenames))
			output_directory = "joined{:d}".format(nf)
		else:
			debug("{} file(s) {} -> {}".format(nf, filenames, output_directory))
		#
		if (keycode != 0) and not keycode: # allow keycode = 0
			error("Invalid keycode for {} files: {}, skipped".format(nf, filenames))
			nff+=nf
			continue
		#
		if nf == 1:
			# simply move the file into the 1-directory
			move(filenames.pop(), output_directory)
		else:
			output_filename = os.path.join(output_directory, str(keycode)+'.PDF')
			sejda_options = ['merge', '-f']+filenames+['-o', output_filename]
			debug("Running '{}' {}".format(sejda_executable, sejda_options)
			try:
				output = check_output([sejda_executable]+sejda_options)
				debug("sejda output: {}".format(output))
			except Exception as e:
				critical("sejda failed: {}".format(e))
				nff+=nf
				continue
			if os.path.exists(output_filename):
				for f in filenames:
					move(f, move_directory)
			else:
				error("Failed to create {}".format(output_filename))
				nff+=nf
	return nff, n
#
if __name__ == '__main__':
	import logging
	logging.basicConfig(level=logging.DEBUG if __debug__ else logging.WARNING)
	#
	from glob import glob
	import sys
	stderr = sys.stderr
	#
	for d in output_directories:
		if not os.path.isdir(d):	os.mkdir(d)
	if not os.path.isdir(move_directory):
		os.mkdir(move_directory)
	#
	args = sys.argv[1:] or glob('*.PDF')
	failures, total = combine_similarly_named_files(args)
	if failures:
		print >>stderr, "{} failures out of {} total files processed".format(failures, totals)
	else:
		print "No errors, OK to delete '{}'".format(move_directory)
#
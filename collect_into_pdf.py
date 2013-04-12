#! env python
"""
Walks through a list of PDFs, combining PDFs with similar names. Processed parts
are then collected into a seperate directory.

PDFs are joined using the Java package sejda. Download it from:
	http://www.sejda.org/
"""

from glob import glob
from itertools import groupby
from logging import debug, info, warning, error, critical
from os import mkdir
import os.path
from shutil import move
from subprocess import check_output
import sys

# Aquacraft keycode logic is found in a small module:
from keycodes import parse_filename

# sejda is used for PDF processing:
executable="sejda-console-1.0.0.M6\\bin\\sejda-console.bat"

# Processed output files will be 
output_directories=['', 'joined1', 'joined2', 'joined3']

# Processed input files will end up in move_directory, and can be deleted:
move_directory='_processed'

def combine_similarly_named_files(*args, **kwargs):
	n, nff, uf = 0, 0, 0
	args = [ f for f in args if f ]
	n = len(args)
	info("{} input files".format(n))
	args.sort(key=parse_filename)
	for keycode, fi in groupby(args, parse_filename):
		filenames=[ f for f in fi if (os.path.splitext(f)[-1].upper() in ('.PDF',)) ]
		nf = len(filenames)
		try:
			output_directory=output_directories[nf]
		except:
			critical("No output directory for {}-size files, {} skipped".format(nf, filenames))
			continue
		else:
			debug("{} file(s) {} -> {}".format(nf, filenames, output_directory))
		#
		if (keycode != 0) and not keycode: # allow keycode = 0
			error("Invalid keycode for {} files: {}, skipped".format(nf, filenames))
			continue
		if len(filenames) < 1:
			warning("No PDF files for keycode {}, skipped".format(keycode))
		elif len(filenames) == 1:
			# simply move the file into the 1-directory
			src=filenames.pop()
			assert not filenames
			move(src, output_directory)
		else:
			output_filename=os.path.join(output_directory, str(keycode)+".PDF")
			try:
				output = check_output([executable, "merge", "-f"]+filenames+["-o", output_filename])
				debug("sejda output: {}".format(output))
			except Exception as e:
				critical("sejda failed: {}".format(e))
			if os.path.exists(output_filename):
				for f in filenames:
					move(f, move_directory)
			else:
				error("Failed to create {}".format(output_filename))
				nff+=len(filenames)
	return nff, n
#
import logging
logging.basicConfig(level=logging.DEBUG if __debug__ else logging.WARNING)
#
for d in output_directories:
	if not os.path.isdir(d):
		mkdir(d)
if not os.path.isdir(move_directory):
	mkdir(move_directory)
#
args = sys.argv[1:] or glob('*.PDF')
failures, total = combine_similarly_named_files(*args)
print "{} failures out of {} total files processed".format(failures, totals)
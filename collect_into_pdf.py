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
import re
from shutil import move
from subprocess import check_output
import sys

from keycodes import Keycode

output_directory='joined'
move_directory='_processed'
extra_keycode_formats = [re.compile('\s*(?P<keycode>\d+)(?P<suffix>[a-zA-Z]\w*)?\s*'),]

def parse_filename(filepath):
	"""
	Filenames are based on keycodes. Some studies used integer IDs, others used
	the 2009 Keycode spec. 
	"""
	if (os.path.sep in filepath) or ('/' in filepath) or (r'\\' in filepath):
		dirname, basename = os.path.split(filepath)
	else:
		basename = filepath
	if os.path.extsep in basename:
		filepart, ext = os.path.splitext(basename)
	else:
		filepart = basename
	id = filepart.upper()
	try:
		id = Keycode(filepart, strict=True)
	except:
		try:
			id = int(filepart[:7])
		except:
			for exp in extra_keycode_formats:
				m = exp.match(filepart)
				if m:
					g = m.groupdict()
					if 'keycode' in g:
						id = int(g['keycode'])
	return id

def combine_similarly_named_files(*args, **kwargs):
	n, nff, uf = 0, 0, 0
	args = [ f for f in args if f ]
	n = len(args)
	info("{} input files".format(n))
	args.sort(key=parse_filename)
	for keycode, fi in groupby(args, parse_filename):
		filenames=[ f for f in fi if (os.path.splitext(f)[-1].upper() in ('.PDF',)) ]
		nf = len(filenames)
		debug("{} file(s) {} -> keycode {}".format(nf, filenames, keycode))
		if keycode in (None, ''):
			error("Invalid keycode for {} files {}, skipped".format(nf, filenames))
			uf+=nf
			continue
		if len(filenames) < 1:
			error("No PDF files for keycode {}, skipped".format(keycode))
			continue
		elif len(filenames) == 1:
			# do nothing
			uf+=1
			continue
		else:
			output_filename=os.path.join(output_directory, "{}.PDF".format(keycode))
			try:
				output = check_output(["sejda-console-1.0.0.M6\\bin\\sejda-console.bat", "merge", "-f"]+filenames+["-o", output_filename])
				debug("sejda output: {}".format(output))
			except Exception as e:
				critical("sejda failed: {}".format(e))
		if os.path.exists(output_filename):
			for f in filenames:
				move(f, move_directory)
		else:
			error("Failed to create {}".format(output_filename))
			nff+=len(filenames)
	if nff:
		warning("{} ignored + {} failed of {} files".format(uf, nff, n))
	else:
		info("{} ignored + {} failed of {} files".format(uf, nff, n))
#
import logging
logging.basicConfig(level=logging.DEBUG if __debug__ else logging.INFO)
#
if not os.path.isdir(output_directory):
	mkdir(output_directory)
if not os.path.isdir(move_directory):
	mkdir(move_directory)
#
args = sys.argv[1:] or glob('*.PDF')
combine_similarly_named_files(*args)
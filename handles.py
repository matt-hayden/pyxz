#! /usr/bin/env python2
"""
Use Sysinternals to find open file handles
"""
from collections import namedtuple
from itertools import groupby
from logging import debug, info, warning, error, critical
import re
import subprocess

def parse_sysinternals_handle_header(iterable, line_number=1, max_lines=6):
	"""
	Returns line number
	"""
	expected_header_lines = """Handle v3.51
Copyright (C) 1997-2013 Mark Russinovich
Sysinternals - www.sysinternals.com
""".splitlines()
	expected_header_lines = """Handle
Copyright
Sysinternals
""".splitlines()
	max_lines = max_lines or len(expected_header_lines)
	for line_number, line in enumerate(iterable, start=line_number):
		# run until expected_header_lines is exhausted:
		if not expected_header_lines:
			return line_number
		# or if exceeding a known cap:
		if line_number > max_lines:
			error("Expected header not encountered after {} lines".format(line_number))
			return line_number
		# empty lines are ignored:
		if not line.strip():
			debug("Empty line {} skipped".format(line_number))
			continue
		else:
			# test against the next value of expected_header_lines
			x = expected_header_lines.pop(0)
			if x.upper() in line.upper():
				info("Header row {}: {}".format(line_number, line))
			else:
				info("Unknown row {}: {}".format(line_number, line))
	return line_number
#
def parse_sysinternals_handle(iterable,
							  line_number=1,
							  factory=namedtuple('SysinternalsHandle', 'executable PID handle_type ID path')):
	"""
	GENERATOR
	"""
	if isinstance(iterable, basestring):
		iterable = iter(iterable.splitlines())
	elif not hasattr(iterable, 'next'):
		iterable = iter(iterable)
	line_number = parse_sysinternals_handle_header(iterable, line_number=1)
	for line_number, line in enumerate(iterable, start=line_number):
		debug(line)
		if line.strip():
			try:
###				### Silly:
#				executable, PID, handle_type, ID = line[:19].rstrip(), int(line[24:29]), line[37:50].rstrip(), int(line[51:55], 16)
#				path = line[57:].rstrip()
#				yield factory(executable, PID, handle_type, ID, path)
				# assume executable cannot contain ': '
				parts = line.split(': ',3)
				executable, _ = re.split(' +pid', parts[0])
				PID, _ = re.split(' +type', parts[1])
				handle_type, ID = re.split(' +', parts[2])
				path = parts[3]
				yield factory(executable, int(PID), handle_type, int(ID, 16), path)
			except Exception as e:
				if 'Initialization error' in line:
					critical('handle did not complete successfully: {}'.format(e))
					critical(line)
					for l in iterable: critical(l)
				raise e
def handle_search(terms, handle_executable='handle.exe'):
	assert terms
	if isinstance(terms, basestring):
		terms = [terms]
	handles = set()
	for t in terms:
		text = subprocess.check_output([handle_executable, t])
		for h in parse_sysinternals_handle(text.splitlines()):
			handles.add(h)
	return handles
def handles_by_pid(*args, **kwargs):
	"""
	GENERATOR
	"""
	s = sorted(handle_search(*args, **kwargs), key=lambda x:x.PID)
	return groupby(s, key=lambda x:x.PID)

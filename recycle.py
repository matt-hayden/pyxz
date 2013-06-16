#!env python
import os.path
import sys

from winshell import delete_file, x_winshell as WinShellException

args = sys.argv[1:]
assert args
for arg in args:
	f = os.path.abspath(arg)
	assert os.path.exists(f)
	try:
		output=delete_file(f, no_confirm=True, silent=True)
	except WinShellException as e:
		print >>sys.stderr, "Deleting", f, "failed with error:", e, "and output", output
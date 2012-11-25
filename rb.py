import sys

from winshell import delete_file, x_winshell

paths = sys.argv[1:]
objs = []
for p in paths:
	try:
		objs.append(delete_file(p, no_confirm=True, silent=True))
	except x_winshell as e:
		print >>sys.stderr, "Deleting", p, "failed with error:", e
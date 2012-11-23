import os, os.path, shutil

"""
Look for directories that have exactly the same name as their parents, then
move into a collection. Useful for the results of zip when extra directories
have been added.
"""

destdir = 'moved'

for r, ds, fs in os.walk('.'):
	for d in ds:
		d = os.path.join(r, d)
		split1 = os.path.split(d)
		split2 = os.path.split(split1[0])
		if split1[-1] == split2[-1]:
			print "Moving", d, "to", destdir
			shutil.move(d, destdir)

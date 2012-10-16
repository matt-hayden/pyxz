import csv
from os.path import join
import sys

expected_header=['Series name', 'File title', 'Directory name', 'File name']
srcroot="%src%"
destroot="%dest%"

with open(sys.argv[-1]) as fi:
	cr=csv.reader(fi)
	header=cr.next()
	if header != expected_header:
		print "Incorrect header found:", header
	else:
		print 'set /p src=Source: '
		print 'set /p dest=Destination: '
		for row in cr:
			series, title, dirname, fn = row
			relpath = join(dirname, fn)
			src=join(srcroot, relpath)
			dest=join(destroot, relpath)
			if __debug__:
				print >> sys.stderr, "Copying", fn, "from", src, "to", dest
			print 'xcopy /h /e /i /d "%s" "%s"' %(src, dest)
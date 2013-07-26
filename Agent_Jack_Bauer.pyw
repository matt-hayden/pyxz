from datetime import datetime, timedelta
import os.path
import sys
import time

from local.xsched import *
from play24 import play24
#
def chime(quietfiles=[".quiet", os.path.expandvars(os.path.expanduser("~/.quiet"))]):
	if filter(os.path.exists, quietfiles):
		sys.exit(0)
	if __debug__:
		print datetime.now(), "==", time.time()
		print "scheduler.queue:"
		for e in scheduler.queue:
			print e
	try:
		play24()
	except:
		sys.exit(-1)
#
if __name__=='__main__':
	try:
#		scheduler.enter(0, 1, chime, ())
		chime
	except Exception as e:
		print >> sys.stderr, "Not running: {}".format(e)
	else:
		enter_repeat(next_hour()-datetime.now(), 1, chime, (), period=timedelta(hours=1))
		scheduler.run()
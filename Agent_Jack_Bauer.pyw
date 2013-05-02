from datetime import datetime, timedelta
import os.path
import sys
import time

from enter_repeat import scheduler, enter_repeat
from play24 import play24
#
def next_hour(now = None, tz = None):
	if not isinstance(now, datetime):
		if now:
			now = datetime.fromtimestamp(now, tz)
		else:
			now = datetime.now(tz)
	return datetime(now.year, now.month, now.day, now.hour, 0, 0) + timedelta(hours=1)
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
	scheduler.enter(0, 1, chime, ())
	enter_repeat(next_hour()-datetime.now(), 1, chime, (), period=timedelta(hours=1))
	scheduler.run()
#!env python
from datetime import datetime, timedelta
import sched
import time

scheduler = sched.scheduler(time.time, time.sleep)

def next_hour(now = None, tz = None):
	if not isinstance(now, datetime):
		if now:
			now = datetime.fromtimestamp(now, tz)
		else:
			now = datetime.now(tz)
	return datetime(now.year, now.month, now.day, now.hour, 0, 0) + timedelta(hours=1)
def enter_repeat(delay, priority, action, argument,
				 period = None):
	"""
	Wrapper for scheduler.enter, taking an extra parameter for the period of
	the timer.
	"""
	if isinstance(delay, timedelta):
		delay = delay.total_seconds()
	if isinstance(period, timedelta):
		period = period.total_seconds()
	if period > 0:
		scheduler.enter(delay, priority-1, enter_repeat,
						(period, priority, action, argument, period)
						)
	scheduler.enter(delay, priority, action, argument)
#

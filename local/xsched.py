#!env python
from datetime import datetime, timedelta
import sched
import time

scheduler = sched.scheduler(time.time, time.sleep)

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

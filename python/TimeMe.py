#!/usr/bin/env python3
from datetime import timedelta, datetime
from contextlib import ContextDecorator
import time

class TimeMeBase:
	"""Very simple state holder
	"""
	initialized = time.time()
	def start(self):
		if self.end: # stopped
			self.begin, self.end = time.time(), 0
			return True
		else: # running
			return False
	def stop(self):
		if self.end: # stopped
			return False
		else: # running
			self.end = time.time()
			self.total += self.end - self.begin
			return True
	@property
	def duration(self):
		if self.end: # stopped
			return self.total
		else: # running
			return self.total + time.time() - self.begin # elapsed time
	def __init__(self, begin=0, total=0):
		self.end = 0 if begin else -1
		self.begin = begin
		self.total = total
	def __str__(self):
		if self.end: # stopped
			return "{} from {} - {}".format(self.duration, datetime.fromtimestamp(self.begin), datetime.fromtimestamp(self.end) )
		else: # running
			return "{} from {}".format(self.duration, datetime.fromtimestamp(self.begin) )
class TimeMe(ContextDecorator, TimeMeBase):
	def __enter__(self):
		self.start()
		return self
	def __exit__(self, *exc):
		return not self.stop()
if __name__ == '__main__':
	with TimeMe() as t:
		print(t)
		print("Hi")
		time.sleep(3)
		print("Hi again")
		print(t)


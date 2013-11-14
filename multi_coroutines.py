#!env python
from collections import Counter, Iterable, namedtuple

import numpy as np

from flatten import flatten

StatRow = namedtuple('StatRow', 'n min max mean stdev sum ss')
def stats_1(initial=None,
			dtype=np.dtype('float'),
			factory=StatRow):
	"""
	
	>>> r = stats_1()
	>>> r.next()		# You must initialize the coroutine like so. You get an empty StatRow:
	StatRow(n=0, min=None, max=None, mean=None, stdev=0.0, sum=0.0, ss=0.0)
	>>> r.send([(1,2,3),6,(4,5)])	# Note that tuples of tuples are flattened
	StatRow(n=6, min=1.0, max=6.0, mean=3.5, stdev=1.707825127659933, sum=21.0, ss=91.0)
	>>> r.next()		# Call next() to retrieve updated stats
	StatRow(n=6, min=1.0, max=6.0, mean=3.5, stdev=1.707825127659933, sum=21.0, ss=91.0)
	
	>>> s = stats_1()
	>>> s.next()
	StatRow(n=0, min=None, max=None, mean=None, stdev=0.0, sum=0.0, ss=0.0)
	>>> s.send(np.arange(100)) # numpy objects are accelerated
	StatRow(n=100, min=0, max=99, mean=49.5, stdev=28.866070047722118, sum=4950.0, ss=328350.0)
	>>> s.send(r.next())		# You can send a StatRow, or the output of a stats_1.next()
	StatRow(n=106, min=0, max=99, mean=46.89622641509434, stdev=29.98739648626082, sum=4971.0, ss=328441.0)
	
	>>> t = stats_1(s.next())	# You can initialize with a StatRow, or the output of a stats_1.next()
	>>> t.next()
	StatRow(n=106, min=0, max=99, mean=46.89622641509434, stdev=29.98739648626082, sum=4971.0, ss=328441.0)
	>>> t.send([1,2,3])
	StatRow(n=109, min=0, max=99, mean=45.660550458715598, stdev=30.470686826199007, sum=4977.0, ss=328455.0)
	"""
	if initial:
		n, min, max, mean, stdev, sum, ss = initial
	else:
		mean = min = max = None
		n, sum, ss, stdev = 0, 0.0, 0.0, 0.0
	while True:
		newval = (yield factory(n, min, max, mean, stdev, sum, ss))
		if newval is None: continue
		elif isinstance(newval, factory):
			n += newval.n
			if newval.min < min: min = newval.min
			if max < newval.max: max = newval.max
			sum += newval.sum
			ss += newval.ss
		elif isinstance(newval, Iterable):
			if isinstance(newval, np.ndarray):
				a = newval
			else:
				a = np.fromiter(flatten(newval), dtype=dtype)
			n += len(a)
			sum += np.sum(a)
			ss += np.sum(a**2)
			my_min, my_max = a.min(), a.max()
			if my_min < min or (min is None): min = my_min
			if max < my_max: max = my_max
		else:
			newval = float(newval)
			n += 1
			sum += newval
			ss += newval**2
			if newval < min or (min is None): min = newval
			if max < newval: max = newval
		mean = sum/n
		variance = ss/n-mean**2
		if variance < 0: variance = 0.0
		stdev = np.sqrt(variance)
#
StatRow2 = namedtuple('StatRow2', 'n min max mode modefreq mean stdev sum ss frequencies')
def stats_2(initial=None,
			dtype=np.dtype('float'),
			factory=StatRow2,
			frequency_decimals=2):
	if isinstance(initial, factory):
		state = initial
	elif initial:
		state = factory(initial)
	else:
		state = factory(0, None, None, None, 0, None, 0.0, 0.0, 0.0, {})
	state.frequencies = Counter(state.frequencies)
	#
	while True:
		newval = (yield state)
		if newval is None: continue
		elif isinstance(newval, factory):
			state.n += newval.n
			state.sum += newval.sum
			state.ss += newval.ss
			state.frequencies.update(newval.frequencies)
		elif isinstance(newval, Iterable):
			if isinstance(newval, np.ndarray):
				a = newval
			else:
				a = np.fromiter(flatten(newval), dtype=dtype)
			state.n += len(a)
			state.sum += np.sum(a)
			state.ss += np.sum(a**2)
			state.frequencies.update(Counter(np.around(a, frequency_decimals)))
			my_min, my_max = np.min(a), np.max(a)
			if my_min < state.min or (state.min is None): state.min = my_min
			if state.max < my_max: state.max = my_max
		else:
			newval = float(newval)
			state.n += 1
			state.sum += newval
			state.ss += newval**2
			state.frequencies[round(newval, frequency_decimals)] += 1
			if newval < state.min or (state.min is None): state.min = newval
			if state.max < newval: state.max = newval
		if __debug__:
			assert state.n == sum(state.frequencies.values())
			assert state.sum == sum(x*f for x,f in state.frequencies.iteritems())
			assert state.ss == sum(x**2*f for x,f in state.frequencies.iteritems())
		state.min, _ = min(state.frequencies)
		state.max, _ = max(state.frequencies)
		(state.mode, state.modefreq), = state.frequencies.most_common(1)
		state.mean = state.sum/state.n
		variance = state.ss/state.n-state.mean**2
		if variance < 0: variance = 0.0
		state.stdev = np.sqrt(variance)
#
class ParametricContainer(object):
	dtype=np.dtype('float')
	frequency_decimals=2
	#
	def __init__(self, initial=None):
		if not initial:
			self.n, self.sum, self.ss, self.frequencies = 0, 0.0, 0.0, Counter()
		elif isinstance(other, ParametricContainer):
			self = other
		elif isinstance(other, Iterable):
			self.from_iterable(other)
	def from_iterable(self, iterable):
		if isinstance(other, np.ndarray):
			a = other
		else:
			a = np.fromiter(flatten(other), dtype=self.dtype)
		self.n += len(a)
		self.sum += np.sum(a)
		self.ss += np.sum(a**2)
		self.frequencies.update(Counter(np.around(a, self.frequency_decimals)))
		my_min, my_max = np.min(a), np.max(a)
		if my_min < self.min or (self.min is None): self.min = my_min
		if self.max < my_max: self.max = my_max
	def update(self, other):
		if not other: return
		elif isinstance(other, ParametricContainer):
			self.frequencies.update(other.frequencies)
			self.n += other.n
			self.sum += other.sum
			self.ss += other.ss
			if other.min < self.min or (self.min is None): self.min=other.min
			if self.max < other.max: self.max=other.max
		else:
			self.update(ParametricContainer(other))

	@property
	def mode(self):
		mode, _ = self.frequencies.most_common(1)
		return mode
	@property
	def mean(self):
		return self.sum/self.n
	@property
	def stdev(self):
		variance = state.ss/state.n-state.mean**2
		if variance < 0: variance = 0
		return np.sqrt(variance)
	
#
if __name__ == '__main__':
	r = stats_1()
	print r.next()
	r.send([(1,2,3),6,(4,5)])
	print r.next()

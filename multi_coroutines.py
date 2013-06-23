#!env python
from collections import namedtuple

import numpy as np

StatRow = namedtuple('StatRow', 'n min max mean stdev sum ss')
def stats_1(initial=None,
			dtype=np.dtype('float'),
			factory=StatRow):
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
			if min < newval.min: min = newval.min
			if max < newval.max: max = newval.max
			sum += newval.sum
			ss += newval.ss
		elif hasattr(newval, '__iter__'):
			a = np.fromiter(newval, dtype=dtype)
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
def multi_coroutines(coroutine,
					 factory_arg = None,
					 initials=[],
					 **kwargs):
	if isinstance(factory_arg, basestring):
		names = factory_arg.split()
		factory = namedtuple('Coroutines', names)
		ndimensions = len(names)
	elif hasattr(factory_arg, '_fields'):
		factory = factory_arg
		ndimensions = factory._fields
	else:
		factory = None
		ndimensions = int(factory_arg)
	assert ndimensions > 0
	runners = []
	if initials:
		assert len(initials)==ndimensions
		runners = [ coroutine(_, **kwargs) for _ in initials ]
	else:
		runners = [ coroutine(**kwargs) for _ in xrange(ndimensions) ]
	while True:
		nexts = [_.next() for _ in runners] # initializes
		newvals = (yield factory(*nexts)) if factory else (yield nexts)
		if newvals is None: continue
		assert len(newvals)==ndimensions
		for d, v in enumerate(newvals):
			runners[d].send(v)

if __name__ == '__main__':
	# 3d test
	#r = multi_coroutines(stats_1, 'A B C')
	r = multi_coroutines(stats_1, 3)
	for _ in r.next():
		print _
	r.send([1,2,3])
	for _ in r.next():
		print _
	r.send([4,5,6])
	for _ in r.next():
		print _
	r.send([(1,2,3),6,(4,5)])
	for _ in r.next():
		print _

#!env python
from collections import Counter, namedtuple

from local.flatten import flatten
from local.xcollections import Namespace
from local.xnp import *

#
def stats_from_frequencies(a):
	class StatResults(Namespace):
		_tuple = tuple
#	class StatResults(CollapsibleNamespace):
#		format='n min max sum ss mean std'.split()
#		_tuple = namedtuple('StatResults', format)
	bins, freq = a['bin'], a['freq']
	r = StatResults()
	r.n = np.sum(freq)
	r.min, r.max = np.min(bins), np.max(bins)
	r.sum = np.sum(bins*freq)
	r.ss = np.sum(bins**2*freq)
	r.mean = r.sum/r.n
	r.var = r.ss/r.n-r.mean**2
	if r.var < 0: r.var = 0
	r.std = np.sqrt(r.var)
	return r

class NumericalCounter(Counter): pass

class StatCounter(NumericalCounter):
	dtype = np.dtype([('bin',np.float), ('freq',np.int)])
	@staticmethod
	def pack_function(_):
		return round(_,4)
	#
	def get_frequencies(self, **kwargs):
		return np.array(self.items(), dtype=self.dtype)
	def get_stats(self, **kwargs):
		a = self.get_frequencies()
		if a.size:
			return stats_from_frequencies(a)
		else: return None
	def get_histogram(self, **kwargs):
		a = self.get_frequencies()
		if a.size:
			return np.histogram(a['bin'], weights=a['freq'], **kwargs)
		else: return None
	def pack(self, function = None, **kwargs):
		"""
		>>> iterable = xrange(100)
		>>> r = StatCounter(iterable)
		>>> print r
		>>>
		"""
		function = function or self.pack_function
		return StatCounter(flatten((function(v),)*f for v,f in self.iteritems()))
#
#class Stats(object)
#
if __name__ == '__main__':
	s = StatCounter(_/43210.0 for _ in xrange(43210))
	s1 = s.get_stats()
	print s1
	p = s.pack()
	p1 = p.get_stats()
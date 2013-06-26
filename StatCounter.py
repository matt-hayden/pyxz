#!env python
from collections import Counter, namedtuple

import numpy as np

StatResults = namedtuple('StatResults', 'n min max mean std')
def stats_from_bin_freq(a):
	bins, freq = a['bin'], a['freq']
	my_n = np.sum(freq)
	my_sum = np.sum(bins*freq)
	my_ss = np.sum(bins**2*freq)
	my_mean = my_sum/my_n
	my_var = my_ss/my_n-my_mean**2
	if my_var < 0: my_var = 0
	my_std = np.sqrt(my_var)
	return StatResults(my_n, np.min(bins), np.max(bins),
					   my_mean, my_std)

class NumericalCounter(Counter):
	# Note: self.elements() provides an iterator!
	pass

class StatCounter(NumericalCounter):
	dtype = np.dtype([('bin',np.float), ('freq',np.int)])
	#
	def get_frequencies(self):
		return np.array(self.items(), dtype=self.dtype)
	def get_stats(self):
		a = self.get_frequencies()
		if a.size:
			return stats_from_bin_freq(a['bin'], a['freq'])
		else: return None
	def get_histogram(self, **kwargs):
		a = self.get_frequencies()
		if a.size:
			return np.histogram(a['bin'], weights=a['freq'], **kwargs)
		else: return None
#
if __name__ == '__main__':
	s = StatCounter([1,2,3])
	print s
	print s.get_stats()
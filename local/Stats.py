#!env python
"""
Rolling parametric statistics

The values comprising a distribution can be discarded after updating a Stats()
object. 

Note: Some other scripts rely on the n member being writable!
"""
import collections
from itertools import izip

import numpy as np
import scipy.stats

import xcsv
import Interval

class StatsError(Exception): pass

class StatsBase(Interval.IntervalBase):
	"""
	Abstract for several classes
	
	Typically, you'd implement:
		n (as a member or a property)
		get_results()
		update() (join two such objects)
	"""
	dtype = np.dtype('float')
	print_format = '.2f'
	#
	def __repr__(self):
		if self: return str(self.get_results())
		else: return "Empty distribution"
	def __len__(self):
		try: return self.n
		except AttributeError: raise StatsError("Uninitialized")
	def __nonzero__(self):
		try: return self.n > 0
		except: return False
	def __ior__(self, other):
		self.update(other)
		return self
class Stats(StatsBase):
	"""
	A class of rolling parametric statistics
	
	
	Maintains these:
		min
		max
	The member properties require these:
		n		Equals len(_)
		sum
		ss		Sum of squared values
	
	Examples:
	
	*** Some arithmetic is supported, like combining two statistical runs:	
	>>> s = Stats([4,5,6])
	>>> s |= Stats([1,2,3])
	>>> s
	StatsResult(n=6, min=1.0, mean=3.5, max=6.0, stdev=1.707825127659933, total=21.0)
	"""
	StatsResult = collections.namedtuple('StatsResult', 'n min mean max stdev total')
	def __init__(self, *args, **kwargs):
		if len(args) == 1 and isinstance(args[0], self.__class__):
			self = args[0]
		elif args:
			self.from_numbers(*args, **kwargs)
	def from_numbers(self, *args, **kwargs):
		if args:
#			if hasattr(args[0], '__iter__'): # Hmm
			if isinstance(args[0], collections.Iterable):
				a = np.fromiter(*args, dtype=self.dtype, **kwargs)
			else:
				a = np.array(args, dtype=self.dtype, **kwargs)
			if len(a):
				self.n, self.min, self.max = len(a), np.min(a), np.max(a)
				self.sum, self.ss = np.sum(a), np.sum(a**2)
	def update(self, *args, **kwargs):
		if not self:
			self, args = Stats(args[0]), args[1:]
		for other in args:
			if isinstance(other, Stats): self._merge(other)
			else: self.update(Stats(other))
	def _merge(self, other):
		self.n += other.n
		self.sum += other.sum
		self.ss += other.ss
		if other.min < self.min:
			self.min = other.min
		if self.max < other.max:
			self.max = other.max
	@property
	def mean(self):
		"""
		>>> Stats(range(100)).mean
		49.5
		"""
		try:
			return self.sum/len(self)
		except AttributeError:
			return None
	@property
	def variance(self):
		"""
		>>> Stats(range(100)).variance
		833.25
		"""
		n = len(self)
		if n > 1:
			v = self.ss/n-self.mean**2
			if v > 0: return v
		return 0.0
	@property
	def sample_variance(self):
		"""
		Unbiased sample variance, an estimation of the variance of the
		population.
		
		>>> Stats([1,2,3]).sample_variance
		3.0
		>>> Stats([1,2]).sample_variance
		0.0
		>>> Stats([1]).sample_variance
		Traceback (most recent call last):
		  ...
		StatsError: invalid calculation for sample variance
		"""
		n = len(self)
		if n > 2:
			v = self.ss/(n-1)-self.mean**2
			return v if v > 0 else 0.0
		elif 1 < n <= 2:
			return 0.0
		else: # Excel raises an error in this case, too
			raise StatsError('invalid calculation for sample variance')
	@property
	def stdev(self):
		return np.sqrt(self.variance)
	@property
	def sample_stdev(self):
		return np.sqrt(self.sample_variance)
	@property
	def cv(self):
		"""
		Mean-centered coefficient of variation
		
		>>> s = Stats(range(100))
		>>> s.cv == 1/s.snr
		True
		"""
		if self.mean:
			return self.stdev/self.mean
	@property
	def snr(self):
		"""
		Signal-to-noise ratio
		
		>>> s = Stats(range(100))
		>>> s.snr == 1/s.cv
		True
		"""
		if self.variance:
			return self.mean/self.stdev
	def confidence(self, alpha, **kwargs):
		"""
		Produce the confidence interval around the mean
		
		>>> s=Stats([1,2,3])
		>>> i=s.confidence(0.05)
		>>> s.mean in i
		True
		>>> a,b=i
		>>> a,b
		(1.9488001302083717, 2.051199869791628)
		"""
		return Interval.Interval(*scipy.stats.norm.interval(alpha, loc=self.mean, scale=self.stdev, **kwargs))
	#
	def get_results(self):
		return self.StatsResult(self.n, self.min, self.mean, self.max, self.stdev, self.sum)
class Distribution(Stats):
	"""
	This could be implemented without numpy using collections.Counter
	"""
	def from_numbers(self, *args, **kwargs):
		self.edges = np.array(kwargs.pop('bins', []))
		if args:
			a = np.fromiter(*args, dtype=self.dtype, **kwargs)
			n = len(a)
			if n:
				self.n, self.sum, self.ss = n, np.sum(a), np.sum(a**2)
				if len(self.edges):
					self.histogram, self.edges = np.histogram(a, bins=self.edges)
					self.min, self.max = np.min(a), np.max(a)
				else:
					self.histogram, self.edges = np.histogram(a)
					self.min, self.max = self.edges[0], self.edges[-1]
	def update(self, *args, **kwargs):
		"""
		Without bins:
		>>> d1=Distribution([1,2,3])
		>>> d2=Distribution([1,2,2,2,2,2,2,2,2,2,2,2,2,3])
		>>> d1 |= d2
		>>> d1
		StatsResult(n=17, min=1.0, mean=2.0, max=3.0, stdev=0.48507125007266599, total=34.0)
		
		With bins:
		>>> d1=Distribution([1,2,3],bins=range(10))
		>>> d2=Distribution([4,5,6],bins=range(10))
		>>> d1
		StatsResult(n=3, min=1.0, mean=2.0, max=3.0, stdev=0.81649658092772626, total=6.0)
		>>> d2
		StatsResult(n=3, min=4.0, mean=5.0, max=6.0, stdev=0.81649658092772681, total=15.0)
		>>> d1 |= d2
		>>> d1
		StatsResult(n=6, min=1.0, mean=3.5, max=6.0, stdev=1.707825127659933, total=21.0)
		>>> d1.histogram
		array([0, 1, 1, 1, 1, 1, 1, 0, 0])
		"""
		if not self:
			self, args = Distribution(args[0]), args[1:]
		for other in args:
			if isinstance(other, Distribution): self._merge(other)
			else: self.update(Distribution(other, bins=self.edges))
	def _merge(self, other):
		# outside bins define limits:
		check = (self.edges[1:-1]==other.edges[1:-1])
		if hasattr(check, 'all'): # it's a numpy.array
			check = check.all()
		if not check:
			raise StatsError("{} is incompatible with {}".format(self.edges, other.edges))
		super(Distribution, self)._merge(other)
		self.histogram += other.histogram
		if other.edges[0] < self.edges[0]:
			self.edges[0] = other.edges[0]
		if self.edges[-1] < other.edges[-1]:
			self.edges[-1] = other.edges[-1]
#		self.min, self.max = self.edges[0], self.edges[-1]
#
class RatioStats(StatsBase):
	"""
	"""
	RatioStatsResults = collections.namedtuple('RatioStatsResults', 'numerator denominator ratio weighted_mean')
	def __init__(self, *args, **kwargs):
		"""
		>>> r = RatioStats([1,2,3],[4,5,6])
		>>> for l, s in zip('numerator denominator ratio weighted_mean'.split(), r.get_results()):
		... 	print l, s
		numerator StatsResult(n=3, min=1.0, mean=2.0, max=3.0, stdev=0.81649658092772626, total=6.0)
		denominator StatsResult(n=3, min=4.0, mean=5.0, max=6.0, stdev=0.81649658092772681, total=15.0)
		ratio StatsResult(n=3, min=0.25, mean=0.3833333333333333, max=0.5, stdev=0.10274023338281633, total=1.1499999999999999)
		weighted_mean 0.4
		"""
		if len(args) == 2:
			self.from_num_denom(*args, **kwargs)
		elif len(args) == 1:
			other, = args
			if isinstance(args[0], self.__class__):
				self = other
			else:
				self.from_num_denom(*other, **kwargs)
		else:
			self.numerator = Distribution()
			self.denominator = Distribution()
			self.ratio = Distribution()
	def from_num_denom(self, num, denom, **kwargs):
		if isinstance(num, Stats):
			raise StatsError("Can only be a scalar or array")
#		elif hasattr(num, '__iter__'):
		elif isinstance(num, collections.Iterable):
			my_num = np.fromiter(num, dtype=self.dtype, **kwargs)
			nbins = kwargs.pop('nbins',[])
			self.numerator = Distribution(my_num, bins=nbins)
		else:
			self.numerator = my_num = float(num)
		#
		if isinstance(denom, Stats):
			raise StatsError("Can only be a scalar or array")
#		elif hasattr(denom, '__iter__'):
		elif isinstance(denom, collections.Iterable):
			my_denom = np.fromiter(denom, dtype=self.dtype, **kwargs)
			dbins = kwargs.pop('dbins', [])
			self.denominator = Distribution(my_denom, bins=dbins)
		else:
			self.denominator = my_denom = float(denom)
		rbins = kwargs.pop('rbins', [])
		self.ratio = Distribution(my_num/my_denom, bins=rbins)
		self.n = self.ratio.n
	def update(self, *args, **kwargs):
		"""
		Unlike Stats() and Distribution(), this takes only one pair of arrays
		at at time.
		
		>>> r = RatioStats()
		>>> r
		Empty distribution
		>>> r.update([1,2,3],[4,5,6])
		>>> for l, s in zip('numerator denominator ratio weighted_mean'.split(), r.get_results()):
		... 	print l, s
		numerator StatsResult(n=3, min=1.0, mean=2.0, max=3.0, stdev=0.81649658092772626, total=6.0)
		denominator StatsResult(n=3, min=4.0, mean=5.0, max=6.0, stdev=0.81649658092772681, total=15.0)
		ratio StatsResult(n=3, min=0.25, mean=0.3833333333333333, max=0.5, stdev=0.10274023338281633, total=1.1499999999999999)
		weighted_mean 0.4
		"""
		if not self:
			self = RatioStats(*args, **kwargs)
			return
		if len(args) == 2:
			num, denom = np.array(args[0]), np.array(args[1]) # a pair of numerator, denominator arrays
			assert len(num) == len(denom)
			self.numerator.update(num)
			self.denominator.update(denom)
			self.ratio.update(num/denom) # array division
			self.n = self.ratio.n
		elif len(args) == 1:
			other, = args
			if isinstance(other, RatioStats): self._merge(other) # right now, calls an error
			else: self.update(other[0], other[1]) # itself a pair of numerator, denominator arrays
		else:
			raise StatsError("RatioStats.update() expects a numerator and denominator array")
	def _merge(self, other):
		raise StatsError("Cannot join two ratio distributions; you'll need the numerator and denominator as arrays.")
	@property
	def min(self): return self.ratio.min
	@property
	def max(self): return self.ratio.max
	@property
	def range(self): return self.ratio.range
	@property
	def prd(self):
		"""
		Price-related differential
		"""
		return self.ratio.mean/self.weighted_mean
	@property
	def weighted_mean(self):
		try:
			return self.numerator.sum/self.denominator.sum
#		except TypeError:
#			return None
		except ZeroDivisionError:
			raise StatsError("denominator has mean 0")
#	def confidence(self, alpha):
#		"""
#		Case 2 of Feiller's approximation. Assumes joint normality (jikes).
#		"""
#		if 0 in self.denominator.confidence(alpha):
#			raise ZeroDivisionError("Denominator confidence interval spans 0")
#		df = len(self)
#		critical_t = scipy.stats.t.isf(alpha, df)
#		g = (critical_t/self.denominator.mean)**2*self.denominator.variance
	def get_results(self):
		return self.RatioStatsResults(self.numerator.get_results(),
									  self.denominator.get_results(),
									  self.ratio.get_results(),
									  self.weighted_mean)
#
def get_table_stats(*args, **kwargs):
	col_stats = collections.defaultdict(Distribution)
	all_stats = Distribution()
	rows = xcsv.load_csv(*args, **kwargs)
	# transpose with izip
	for n, col in enumerate(izip(*rows)):
		dist = Distribution(col)
		print "Updating", col_stats[n], "with", dist
		col_stats[n].update(dist)
		all_stats.update(dist)
	return all_stats, col_stats
#
if __name__ == '__main__':
	import sys
	
	args = sys.argv[1:]
	for arg in args:
		print arg
		print get_table_stats(arg, dialect='excel-tab')
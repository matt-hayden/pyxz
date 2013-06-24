#!env python
import numpy as np
import scipy.stats

from Interval import IntervalBase, Interval

class StatsBase(IntervalBase):
	dtype = np.dtype('float')
	print_format = '.2f'
	#
	def __len__(self):
		try: return self.n
		except AttributeError:
			raise ValueError("Empty distribution")
	def __nonzero__(self):
		try: return self.n > 0
		except: return False
	def __iand__(self, other):
		self.update(other)
		return self
class Stats(StatsBase):
	"""
	Maintains these:
		min
		max
	The member properties require these:
		n		Equals len(_)
		sum
		ss		Sum of squared values
	
	Examples:
	Combine another statistical run with this one:
	
	>>> s = Stats([4,5,6])
	>>> s &= Stats([1,2,3])
	>>> s
	n=6.00 min=1.00 mean=3.50 max=6.00 stdev=1.71 total=21.00
	"""
	def __init__(self, *args, **kwargs):
		if len(args) == 1 and isinstance(args[0], self.__class__):
			self = args[0]
		elif args:
			self.from_numbers(*args, **kwargs)
	def from_numbers(self, *args, **kwargs):
		if args:
			if hasattr(args[0], '__iter__'): # Hmm
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
		ZeroDivisionError: invalid calculation for sample variance
		"""
		n = len(self)
		if n > 2:
			v = self.ss/(n-1)-self.mean**2
			return v if v > 0 else 0.0
		elif 1 < n <= 2:
			return 0.0
		else: # Excel raises an error in this case, too
			raise ZeroDivisionError('invalid calculation for sample variance')
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
		return Interval(*scipy.stats.norm.interval(alpha, loc=self.mean, scale=self.stdev, **kwargs))
	#
	def __repr__(self):
		if self:
			parts = (('n', self.n),
					 ('min', self.min),
					 ('mean', self.mean),
					 ('max', self.max),
					 ('stdev', self.stdev),
					 ('total', self.sum))
			try:
				return ' '.join("{0}={1:{2}}".format(p,v,self.print_format) for p,v in parts)
			except:
				return ' '.join("{0}={1}".format(p,v) for p,v in parts)
		else:
			return "Empty distribution"
class Distribution(Stats):
	"""
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
		>>> d1 &= d2
		>>> d1
		n=17.00 min=1.00 mean=2.00 max=3.00 stdev=0.49 total=34.00
		
		With bins:
		>>> d1=Distribution([1,2,3],bins=range(10))
		>>> d2=Distribution([4,5,6],bins=range(10))
		>>> d1
		n=3.00 min=1.00 mean=2.00 max=3.00 stdev=0.82 total=6.00
		>>> d2
		n=3.00 min=4.00 mean=5.00 max=6.00 stdev=0.82 total=15.00
		>>> d1 &= d2
		>>> d1
		n=6.00 min=1.00 mean=3.50 max=6.00 stdev=1.71 total=21.00
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
			raise ValueError("{} is incompatible with {}".format(self.edges, other.edges))
		super(Distribution, self)._merge(other)
		self.histogram += other.histogram
		if other.edges[0] < self.edges[0]:
			self.edges[0] = other.edges[0]
		if self.edges[-1] < other.edges[-1]:
			self.edges[-1] = other.edges[-1]
#
class RatioStats(StatsBase):
	def __init__(self, *args, **kwargs):
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
			self.ratio_stats = Distribution()
	def from_num_denom(self, num, denom, **kwargs):
		bins = kwargs.pop('bins',([], [], []))
		assert len(bins) == 3
		if isinstance(num, Stats):
			raise ValueError("Can only be a scalar or array")
		elif hasattr(num, '__iter__'):
			my_num = np.fromiter(num, dtype=self.dtype, **kwargs)
			nbins = kwargs.pop('nbins', bins[0])
			self.numerator = Distribution(my_num, bins=nbins)
		else:
			self.numerator = my_num = float(num)
		#
		if isinstance(denom, Stats):
			raise ValueError("Can only be a scalar or array")
		elif hasattr(denom, '__iter__'):
			my_denom = np.fromiter(denom, dtype=self.dtype, **kwargs)
			dbins = kwargs.pop('dbins', bins[1])
			self.denominator = Distribution(my_denom, bins=dbins)
		else:
			self.denominator = my_denom = float(denom)
		rbins = kwargs.pop('rbins', bins[2])
		self.ratio_stats = Distribution(my_num/my_denom, bins=rbins)
		self.n = len(self.ratio_stats)
	def update(self, *args, **kwargs):
		"""
		Unlike Stats() and Distribution(), this takes only one pair of arrays
		at at time.
		
		>>> r = RatioStats()
		>>> r
		numerator: Empty distribution
		denominator: Empty distribution
		ratio: Empty distribution
		weighted mean: None
		>>> r.update([1,2,3],[4,5,6])
		>>> r
		numerator: n=3.00 min=1.00 mean=2.00 max=3.00 stdev=0.82 total=6.00
		denominator: n=3.00 min=4.00 mean=5.00 max=6.00 stdev=0.82 total=15.00
		ratio: n=3.00 min=0.25 mean=0.38 max=0.50 stdev=0.10 total=1.15
		weighted mean: 0.4
		"""
		if not self:
			self = Distribution(*args, **kwargs)
			return
		if len(args) == 2:
			num, denom = np.array(args[0]), np.array(args[1])
			self.numerator.update(num)
			self.denominator.update(denom)
			self.ratio_stats.update(num/denom)
		elif len(args) == 1:
			other, = args
			if isinstance(other, RatioStats): self._merge(other) # calls an error
			else: self.update(other[0], other[1])
		else:
			raise NotImplementedError("RatioStats.update() expects a numerator and denominator array")
	def _merge(self, other):
		raise NotImplementedError("Cannot join two ratio distributions; you'll need the numerator and denominator as arrays.")
	@property
	def min(self):
		return self.ratio_stats.min
	@property
	def max(self):
		return self.ratio_stats.max
	@property
	def range(self):
		return self.ratio_stats.range
	@property
	def prd(self):
		"Price-related differential"
		return self.ratio_stats.mean/self.weighted_mean
	@property
	def weighted_mean(self):
		try:
			return self.numerator.mean/self.denominator.mean
		except TypeError:
			return None
		except ZeroDivisionError:
			return None
#	def confidence(self, alpha):
#		"""
#		Case 2 of Feiller's approximation. Assumes joint normality (jikes).
#		"""
#		if 0 in self.denominator.confidence(alpha):
#			raise ZeroDivisionError("Denominator confidence interval spans 0")
#		df = len(self)
#		critical_t = scipy.stats.t.isf(alpha, df)
#		g = (critical_t/self.denominator.mean)**2*self.denominator.variance
	def __repr__(self):
		"""
		>>> print RatioStats(range(100), range(100,200))
		numerator: n=100.00 min=0.00 mean=49.50 max=99.00 stdev=28.87 total=4950.00
		denominator: n=100.00 min=100.00 mean=149.50 max=199.00 stdev=28.87 total=14950.00
		ratio: n=100.00 min=0.00 mean=0.30 max=0.50 stdev=0.14 total=30.43
		weighted mean: 0.33110367893
		"""
		parts = (('numerator', repr(self.numerator)),
				 ('denominator', repr(self.denominator)),
				 ('ratio', repr(self.ratio_stats)),
				 ('weighted mean', self.weighted_mean))
		return '\n'.join("{0}: {1}".format(x,y) for x,y in parts)
#
#
if __name__ == '__main__':
	import doctest
	doctest.testmod()

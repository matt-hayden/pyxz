#!env python
import numpy
import scipy.stats

from Interval import IntervalBase, Interval

class StatsBase(IntervalBase):
	dtype = numpy.dtype('float')
	print_format = '.2f'
	#
	def __len__(self):
		try: return self.n
		except AttributeError:
			raise ValueError("Empty distribution")
	def __nonzero__(self):
		try: return self.n > 0
		except: return False
class Stats(StatsBase):
	"""
	Maintains these:
		min
		max
	The member properties require these:
		n		Equals len(_)
		sum
		ss		Sum of squared values
	"""
	def __init__(self, *args, **kwargs):
		super(Stats, self).__init__()
		self.from_numbers(*args, **kwargs)
	def from_numbers(self, *args, **kwargs):
		if args:
			if hasattr(args[0], '__iter__'):
				a = numpy.fromiter(*args, dtype=self.dtype, **kwargs)
			else:
				a = numpy.array(args, dtype=self.dtype, **kwargs)
			if len(a):
				try:
					self.n, (self.min, self.max), my_mean, my_var, self.skew, self.kurt = scipy.stats.describe(a)
				except:
					self.n, self.min, self.max = len(a), numpy.min(a), numpy.max(a)
				self.sum, self.ss = numpy.sum(a), numpy.sum(a**2)
	def update(self, *args, **kwargs):
		for other in args:
			if isinstance(other, Stats):
				self.n += other.n
				self.sum += other.sum
				self.ss += other.ss
				if other.min < self.min:
					self.min = other.min
				if self.max < other.max:
					self.max = other.max
			else:
				self.update(Stats(other))
	@property
	def mean(self):
		"""
		>>> Stats(range(100)).mean
		49.5
		"""
		if self.sum: return self.sum/len(self)
		else: return 0.0
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
		return numpy.sqrt(self.variance)
	@property
	def sample_stdev(self):
		return numpy.sqrt(self.sample_variance)
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
	def __and__(self, other):
		"""
		This is how you combine two statistical runs into one:
		
		>>> Stats([1,2,3]) & Stats([-3,-2,-1])
		n=6.00 min=-3.00 mean=0.00 max=3.00 stdev=2.16 total=0.00
		"""
		r = Stats()
		r.n = self.n+other.n
		r.sum = self.sum+other.sum
		r.ss = self.ss+other.ss
		r.min = min(self.min, other.min)
		r.max = max(self.max, other.max)
		return r
	def __iand__(self, other):
		"""
		Combine another statistical run with this one:
		
		>>> s = Stats([4,5,6])
		>>> s &= Stats([1,2,3])
		>>> s
		n=6.00 min=1.00 mean=3.50 max=6.00 stdev=1.71 total=21.00
		
		"""
		self.update(other)
		return self
	def __repr__(self):
		if self:
			parts = (('n', self.n),
					 ('min', self.min),
					 ('mean', self.mean),
					 ('max', self.max),
					 ('stdev', self.stdev),
					 ('total', self.sum))
			try:
				return ' '.join("{0}={1:{2}}".format(x,y,self.print_format) for x,y in parts)
			except:
				return ' '.join("{0}={1}".format(x,y) for x,y in parts)
		else:
			return "Empty distribution"
class Distribution(Stats):
	"""
		frequencies:	a list of (score, freq) pairs, not necessarily unique
	"""
	def from_numbers(self, *args, **kwargs):
		if args:
			a = numpy.fromiter(*args, dtype=self.dtype, **kwargs)
			if len(a):
				try:
					self.n, (my_min, my_max), my_mean, my_var, self.skew, self.kurt = scipy.stats.describe(a)
				except:
					self.n = len(a)
				self.sum, self.ss = numpy.sum(a), numpy.sum(a**2)
				self.frequencies = scipy.stats.itemfreq(a)
	def histogram(self, **kwargs):
		return scipy.stats.histogram([_[0] for _ in self.frequencies], weights=[_[1] for _ in self.frequencies], **kwargs)
	def update(self, *args, **kwargs):
		for other in args:
			if isinstance(other, Distribution):
				self.n += other.n
				self.frequencies = numpy.concatenate((self.frequencies, other.frequencies))
			else:
				self.update(Distribution(other))
###
### These are very, very slow:
###
	def filter(self, filter_function):
		values = ()
		for score, freq in self.frequencies:
			if filter_function(score):
				values += (score,)*freq
		return Distribution(values)
	@property
	def values(self):
		for score, freq in self.frequencies:
			for i in xrange(int(freq)):
				yield score
	def map(self, map_function):
		values = ()
		for score, freq in self.frequencies:
			values += (map_function(score),)*freq
		return Distribution(values)
	def percentile(self, per, **kwargs):
		return scipy.stats.scoreatpercentile(list(self.values), per, **kwargs)
###
###
###
	def __mod__(self, per):
		return self.percentile(per)
	@property
	def min(self):
		return self % 0
	@property
	def median(self):
		return self % 50
	@property
	def max(self):
		return self % 100
	def trim(self, per):
		lower=(100-per)/2
		upper=(100-lower)
		return self.filter(lambda _: (self % lower) <= _ <= (self % upper))
	#
	def __iand__(self, other):
		super(Distribution, self).__iand__(other)
		self.frequencies = numpy.concatenate((self.frequencies, other.frequencies))
		return self
	def __and__(self, other):
		r = super(Distribution, self).__and__(self, other)
		r.frequencies = numpy.concatenate((self.frequencies, other.frequencies))
		return r
class RatioStats(StatsBase):
	def __init__(self, *args, **kwargs):
		if args:
			self.from_num_denom(*args, **kwargs)
	def from_num_denom(self, num, denom, **kwargs):
		if hasattr(num, '__iter__'):
			my_num = numpy.fromiter(num, dtype=self.dtype, **kwargs)
			self.numerator = Distribution(my_num)
			assert self.numerator
		else:
			self.numerator = my_num = float(num)
		if hasattr(denom, '__iter__'):
			my_denom = numpy.fromiter(denom, dtype=self.dtype, **kwargs)
			self.denominator = Distribution(my_denom)
			assert self.denominator
		else:
			self.denominator = my_denom = float(denom)
		self.ratio_stats = Distribution(my_num/my_denom)
		self.n = len(self.ratio_stats)
	def update(self, num, denom):
		self.numerator.update(num)
		self.denominator.update(denom)
		self.ratio_stats.update(num/denom)
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
	def median(self):
		return self.ratio_stats % 50
	@property
	def prd(self):
		"Price-related differential"
		return self.ratio_stats.mean/self.weighted_mean
	@property
	def weighted_mean(self):
		return self.numerator.mean/self.denominator.mean
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

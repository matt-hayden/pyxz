#!env python
import numpy
try:
	import scipy.stats
except:
	pass

from Interval import Interval

class Stats(Interval):
	"""
	Maintains these:
		min
		max
		median
	The member properties require these:
		n		Equals len(_)
		sum
		ss		Sum of squared values
	"""
	dtype = numpy.dtype('float')
	print_format = '.2f'
	def __init__(self, *args, **kwargs):
		self.from_numbers(*args, **kwargs)
	def from_numbers(self, *args, **kwargs):
#		h = kwargs.pop('save_distribution', False)
		if args:
			a = numpy.fromiter(*args, dtype=self.dtype, **kwargs)
			try:
				self.n, (self.min, self.max), my_mean, my_var, self.skew, self.kurt = scipy.stats.describe(a)
			except:
				self.n, self.min, self.max = len(a), numpy.min(a), numpy.max(a)
			self.sum, self.ss = numpy.sum(a), numpy.sum(a**2)
#			self.median = numpy.median(a)
	def __len__(self):
		return self.n
	def __nonzero__(self):
		try:
			return self.n > 0
		except:
			return False
	@property
	def mean(self):
		"""
		>>> Stats(range(100)).mean
		49.5
		"""
		return self.sum/len(self)
	@property
	def variance(self):
		return self.ss/len(self)-self.mean**2
	@property
	def sample_variance(self):
		return self.ss/(len(self)-1)-self.mean**2
	@property
	def stdev(self):
		return numpy.sqrt(self.variance)
	@property
	def sample_stdev(self):
		return numpy.sqrt(self.sample_variance)
	def confidence(self, alpha):
		return Interval(*scipy.stats.norm.interval(alpha, loc=self.mean, scale=self.stdev))
	def __and__(self, other):
		"""
		This is how you combine two statistical runs into one:
		
		>>> Stats([1,2,3]) & Stats([-3,-2,-1])
		n=6.00 min=-3.00 mean=0.00 max=3.00 stdev=2.16
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
		n=6.00 min=1.00 mean=3.50 max=6.00 stdev=1.71
		
		"""
		self.n += other.n
		self.sum += other.sum
		self.ss += other.ss
		if other.min < self.min:
			self.min = other.min
		if self.max < other.max:
			self.max = other.max
#		del self.median
		return self
	def __repr__(self):
		if self:
			parts = (('n', self.n),
					 ('min', self.min),
					 ('mean', self.mean),
					 ('max', self.max),
					 ('stdev', self.stdev))
			return ' '.join(["{0}={1:{2}}".format(x,y,self.print_format) for x,y in parts])
		else:
			return "Empty statistics"
class distribution(Stats):
	def from_numbers(self, *args, **kwargs):
		if args:
			a = numpy.fromiter(*args, dtype=self.dtype, **kwargs)
			self.frequencies = scipy.stats.itemfreq(a)
			super(distribution, self).__init__(a, **kwargs)
	def histogram(self, bins = None):
		return scipy.stats.histogram([_[0] for _ in self.frequencies], weights=[_[1] for _ in self.frequencies])
	def __or__(self, filter_function):
		values = ()
		for score, freq in self.frequencies:
			if filter_function(score):
				values += (score,)*freq
		return distribution(values)
	@property
	def values(self):
		values = ()
		for score, freq in self.frequencies:
			values += (score,)*freq
		return values
	def percentile(self, per, **kwargs):
		return scipy.stats.scoreatpercentile(self.values, per, **kwargs)
	def __mod__(self, per):
		return self.percentile(per)
	def trim(self, alpha):
		lower=(1-alpha)/2
		upper=(1-lower)
		return self | (lambda _: lower <= _ <= upper)
class RatioStats:
	def __init__(self, *args, **kwargs):
		self.from_num_denom(*args, **kwargs)
	def from_num_denom(self, num, denom):
		my_num = numpy.fromiter(num)
		my_denom = numpy.fromiter(denom)
		assert len(my_num) == len(my_denom)
		self.numerator = Stats(my_num)
		self.denominator = Stats(my_denom)
		self.ratio_stats = Stats(my_num/my_denom)
	@property
	def mean_rate(self):
		return self.numerator.sum/self.denominator.sum
	
		
#
if __name__ == '__main__':
	import doctest
	doctest.testmod()

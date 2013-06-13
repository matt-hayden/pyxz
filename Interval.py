#!env python

class Interval(object):
	"""
	Closed one-dimensional interval object. Arithmetic will not work on ordered
	pairs.
	"""
	__slots__ = ['min', 'max']
	def __init__(self, min, max):
		self.min, self.max = min, max
	def to_tuple(self):
		return (self.min, self.max)
	@property
	def midpoint(self):
		return (self.max + self.min)/2
	@property
	def range(self):
		return self.max - self.min
	def ints(self):
		return xrange(int(self.min), int(self.max)+1)
	#
	def __iter__(self):
		"""
		Acts like a tuple when unpacking
		
		>>> a,b = Interval(0,1)
		>>> a,b
		(0, 1)
		"""
		return iter(self.to_tuple())
	def __contains__(self, object):
		"""
		>>> 1.5 in Interval(0,3)
		True
		>>> Interval(1,2) in Interval(0,3)
		True
		"""
		if isinstance(object, Interval):
			return (self.min <= object.min and object.max <= self.max)
		else:
			return self.min <= object <= self.max
	def __nonzero__(self):
		"""
		Intervals consisting of a single point resolve to True. Unset or invalid
		ranges resolve to False.
		"""
		try:
			return self.range >= 0
		except:
			return False
	def __repr__(self):
		return self.__class__.__name__+str(self.to_tuple())
	def __and__(self, other):
		return intersection(self, other)
	def __or__(self, other):
		"""
		For overlapping sets, returns an Interval covering both arguments.
		
		>>> Interval(0,1) | Interval(1,2)
		Interval(0, 2)
		>>> Interval(0,2) | Interval(1,2)
		Interval(0, 2)
		>>> Interval(0,2) | Interval(10,20)
		[]
		"""
		return intersection(self, other) and cover(self, other)
	def __rmul__(self, scalar): # left-to-right is reversed here
		"""
		>>> 6*Interval(1,2)
		Interval(6, 12)
		"""
		return Interval(scalar*self.min, scalar*self.max)
	def __mul__(self, scalar):
		return scalar*self
	def __invert__(self):
		"""
		>>> ~Interval(1,2)
		Interval(0.5, 1.0)
		>>> ~Interval(-1,1)
		Traceback (most recent call last):
		  ...
		AssertionError
		"""
		assert 0 not in self
		return Interval(1.0/self.max, 1.0/self.min)
def cover(*args):
	return Interval(min(_.min for _ in args), max(_.max for _ in args))
def intersection(*args):
	lower, upper = max(_.min for _ in args), min(_.max for _ in args)
	if all(lower in _ for _ in args) and all(upper in _ for _ in args):
		return Interval(lower, upper)
	else:
		return []
#
if __name__ == '__main__':
	import doctest
	doctest.testmod()
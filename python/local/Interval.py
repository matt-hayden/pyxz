#!env python
"""Generalization of objects that inclusively span from a min to a max.
"""

class EasyToPickle(object):
	### subclasses should define to_tuple()
	def __repr__(self):
		return self.__class__.__name__+str(self.to_tuple())
	def __reduce__(self):
		### return a text representation or a tuple like (Interval, args)
		return (self.__class__, self.to_tuple())
class IntervalBase(object):
	"""
	Closed one-dimensional interval object. Arithmetic will not work on ordered
	pairs.
	"""
	__slots__ = ['min', 'max']
	### subclasses should define zero
	#
	def to_tuple(self):
		return (self.min, self.max)
	def to_dict(self):
		return {'min':self.min, 'max':self.max}
	def __eq__(self, other):
		"""
		>>> Interval(0,1) == Interval(0,1)
		True
		"""
		return self.to_tuple() == other.to_tuple()
	@property
	def midpoint(self):
		return (self.max + self.min)/2
	@property
	def range(self):
		return self.max - self.min
	def ints(self):
		return xrange(int(self.min), int(self.max)+1)
	def __contains__(self, object):
		"""
		>>> 1.5 in Interval(0,3)
		True
		>>> Interval(1,2) in Interval(0,3)
		True
		"""
		if isinstance(object, IntervalBase):
			return (self.min <= object.min and object.max <= self.max)
		else:
			return self.min <= object <= self.max
	def __nonzero__(self):
		"""
		Intervals consisting of a single point resolve to True. Unset or invalid
		ranges resolve to False.
		"""
		try: return self.range >= self.zero
		except: return False
	@property
	def reciprocal(self):
		"""
		>>> Interval(1,2).reciprocal
		Interval(0.5, 1.0)
		>>> Interval(-1,1).reciprocal
		Traceback (most recent call last):
		  ...
		ZeroDivisionError: Interval spans 0
		"""
		if self.zero in self: raise ZeroDivisionError("Interval spans 0")
		return Interval(1.0/self.max, 1.0/self.min)
class Interval(IntervalBase, EasyToPickle):
	"""
	Pickling works as expected:
	
	>>> import cPickle as pickle
	>>> i = Interval(0,1)
	>>> s = pickle.dumps(i)
	>>> pickle.loads(s) == i
	True
	"""
	zero = 0.0
	#
	def __init__(self, min, max):
		self.min, self.max = min, max
	def __iter__(self):
		"""
		Acts like a tuple when unpacking
		
		>>> a,b = Interval(0,1)
		>>> a,b
		(0, 1)
		"""
		return iter(self.to_tuple())
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
###
### I'm not exactly sure this is the right way to do the scalar multiplication
### syntax.
###
	def __rmul__(self, scalar): # left-to-right is reversed here
		"""
		>>> 6*Interval(1,2)
		Interval(6, 12)
		"""
		return Interval(scalar*self.min, scalar*self.max)
	def __mul__(self, scalar):
		return scalar*self
def cover(*args):
	return Interval(min(_.min for _ in args), max(_.max for _ in args))
def intersection(*args):
	lower, upper = max(_.min for _ in args), min(_.max for _ in args)
	if all(lower in _ for _ in args) and all(upper in _ for _ in args):
		return Interval(lower, upper)
	else: return []
#
if __name__ == '__main__':
	import doctest
	doctest.testmod()
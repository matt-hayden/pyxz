
def is_range(iterable, if_empty=False):
	"""
	True if the argument is equivalent to an integer interval. Behaviour for
	empty sets is the argument if_empty.
	"""
	try:
		intset = set(int(_) for _ in iterable)
	except:
		return False
	n = len(intset)
	if n == 0: return if_empty
	elif n == 1: return True
	else:
		my_min, my_max = min(intset), max(intset)
#		if my_min == my_max: return True # unreachable?
		for i in xrange(my_min+1, my_max): # loops from [1] to [-2]
			if i not in intset: return False
		return True

# Neat trick to make simple namespaces:
# http://stackoverflow.com/questions/4984647/accessing-dict-keys-like-an-attribute-in-python
class Namespace(dict):
	"""
	An abstract class. Inheriting from this limits your class' functionality,
	but allows i['j'] and i.j to be assigned and used interchangably.
	>>> n=Namespace()
	>>> n.blues = 'brothers'
	>>> n['blues'] == 'brothers'
	True
	>>> n
	{'blues': 'brothers'}
	
	Pickling should work as expected:
	>>> import cPickle as pickle
	>>> s = pickle.dumps(n)
	>>> s2 = pickle.loads(s)
	>>> s2
	{'blues': 'brothers'}
	"""
#	__slots__ = [ '__dict__' ] # sabotages pickle :)
	def __init__(self, *args, **kwargs):
		super(Namespace, self).__init__(*args, **kwargs)
		self.__dict__ = self
class Collapsible(object):
	# subclasses should define to_tuple()
	def __repr__(self):
		return self.__class__.__name__+str(self.to_tuple())
	def __reduce__(self):
		# return a text representation or a tuple like (Foo, args)
		return (self.__class__, self.to_tuple())
class CollapsibleNamespace(Namespace, Collapsible):
	def to_tuple(self, format=None):
		if format is None:
			try:
				format = self.format
			except:
				format = self._tuple._fields
		elif isinstance(format, basestring): format = format.split()
#		else: # format's doin just fine
		return self._tuple(*[self[_] for _ in format])
if __name__ == '__main__':
	import doctest
	results = doctest.testmod()
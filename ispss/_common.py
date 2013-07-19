#! env python
"""
Helper functions callable within SPSS. This file is for functions that do not
require external dependencies besides the Python standard library.
"""
def first(*args, **kwargs):
	factory=kwargs.pop('factory', float)
	for arg in args:
		try:
			return factory(arg)
		except ValueError:
			pass
	return kwargs.pop('default', None)
def last(*args, **kwargs):
	return first(*reversed(args), **kwargs)

def sjoin(*args, **kwargs):
	"""
	Use like this:
		spssinc trans
		result=a255
		type=255
		/formula sjoin(..., ...)
		.
	"""
	factory = kwargs.pop('factory', str) # or long, e.g.
	ignore_strings = kwargs.pop('ignore_strings',('NULL', '#NULL!')) # a-la Excel and databases
	sep = kwargs.pop('sep', ';')
	#
	r = []
	for a in args:
		# a is long, str, float, None or maybe Decimal
		# s is the string representation, if it exists
		# f is the factory representation, if it exists
		try:
			s = str(a).strip()
		except:
			s = ""
		if a and s and s.upper() not in ignore_strings:
			try:
				f = factory(a)
				if f:
					r.append(f)
			except Exception as e:
				print "Factory {!r} cannot parse {}: {}".format(factory, a, e)
	return sep.join(r) if (factory == str) else sep.join(str(e) for e in r)
### Dies in SPSS, "long object not iterable"
# def ijoin(*args, **kwargs):
	# factory = kwargs.pop('factory', lambda x: long(float(x)))
	# try:
		# s = sjoin(*args, **kwargs)
	# except:
		# print "Unable to parse", args
	# try:
		# return factory(s)
	# except:
		# if s:
			# print "'{}' not converted".format(s)
		# return None
def find_numbers(text):
	numbers = []
	for t in text.split():
		if t[-1] not in '0123456789':
			t=t[:-1]
		try:
			numbers.append(float(t))
		except ValueError:
			if t:
				print "'{}' not a number".format(t)
	return numbers
def keyword_matches(text, *keywords):
	if keywords:
		text = text.upper()
		return [_.upper() in text for _ in keywords]
	else:
		return []

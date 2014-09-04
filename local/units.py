#!env python
"""Custom unit tagging and conversion.
"""
from collections import OrderedDict
from math import *

metric_prefixes = ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
metric_divisors = OrderedDict((s,10**(3*i)) for i,s in enumerate(metric_prefixes))
binary_prefixes = ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi']
binary_divisors = OrderedDict((s,(1 << i*10)) for i,s in enumerate(binary_prefixes))

def human_readable_bytes(size, base=1000, isexp=False):
	"""
	Positive and negative units of bytes. Use base=1024 for iB notation, which
	should only be used when referencing units of RAM where memory cells are
	conventionally paired.
	
	>>> print human_readable_bytes(1+1e+17)
	(100.0000000000002, 'PB')
	>>> print human_readable_bytes(1)
	(1.0, 'B')
	>>> print human_readable_bytes(-123456789)
	(-123.45678900000014, 'MB')
	>>> print human_readable_bytes(1+1e+24)
	(1.0, 'YB')
	
	Beyond the largest category, you can expect large values with the last unit.
	>>> print human_readable_bytes(1+1000*1e+24)
	(1000.0, 'YB')
	
	For very big numbers that are already logged in the indicated base, use the
	'isexp' flag. I.e. 1000**5.666666666666667 equals 1e+17. 
	>>> human_readable_bytes(5.666666666666667, isexp=True) == human_readable_bytes(1e+17)
	True
	>>> human_readable_bytes(0, isexp=True)
	(1, 'B')
	
	Of course, log values less than 0 are impossible.
	>>> human_readable_bytes(-123456789, isexp=True)
	Traceback (most recent call last):
		...
	ValueError: expicit log argument was negative: math domain error
	"""
	if not (base % 10):
		base = 10**3
		divisors, prefixes = metric_divisors, metric_prefixes
	elif not (base % 16):
		base = 2**10
		divisors, prefixes = binary_divisors, binary_prefixes
	if isexp:
		if size < 0:
			raise ValueError("expicit log argument was negative: math domain error") 
		logsize, pos = size, True
	else:
		if size == 0:
			return 0, prefixes[0]+'B'
		elif size < 0:
			size, pos = -size, False
		else:
			pos = True
		logsize = log(size, base)
	exp, maxexp = trunc(logsize), len(prefixes)-1
	exp = min(exp, maxexp)
	m = base**(logsize-exp)
	return m if pos else -m, prefixes[exp]+'B'
### Much slower method:
#	size = factory(size)
#	for p in divisors.keys()[:-1]:
#		if size < base: return size, p+'B'
#		else: size /= base
#	return size, divisors.keys()[-1]+'B'

def kelvin_to_celsius(k):
	return k-273.15
def celsius_to_fahrenheit(c):
	return 9*c/5+32
def kelvin_to_fahrenheit(k):
	return celsius_to_fahrenheit(kelvin_to_celsius(k))
def direction_name(angle, units='degrees'):
	if units.lower().startswith('deg'):
		angle = radians(angle)
	angle %= 2*pi
	threshold = 0.975*(pi/8)
	#
	n_to_s, w_to_e = cos(angle), sin(angle)
	if abs(n_to_s) < threshold:
		n_part = ""
	elif (0 < n_to_s):
		n_part = "N"
	else:
		n_part = "S"
	#
	if abs(w_to_e) < threshold:
		w_part = ""
	elif (0 < w_to_e):
		w_part = "W"
	else:
		w_part = "E"
	return n_part+w_part
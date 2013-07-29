#!env python
from collections import OrderedDict
from math import *

log_bytes_by_prefix = ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
bytes_by_prefix = OrderedDict((s,10**(3*i)) for i,s in enumerate(log_bytes_by_prefix))
log_ibytes_by_prefix = ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi']
ibytes_by_prefix = OrderedDict((s,(1 << i*10)) for i,s in enumerate(log_ibytes_by_prefix))

def byte_units(size, base=1000, isexp=False):
	"""
	Positive and negative units of bytes. Use base=1024 for iB notation, which
	should only be used when referencing units of RAM where memory cells are
	conventionally paired.
	
	>>> print byte_units(1+1e+17)
	(100.0000000000002, 'PB')
	>>> print byte_units(1)
	(1.0, 'B')
	>>> print byte_units(-123456789)
	(-123.45678900000014, 'MB')
	>>> print byte_units(1+1e+24)
	(1.0, 'YB')
	
	Beyond the largest category, you can expect large values with the last unit.
	>>> print byte_units(1+1000*1e+24)
	(1000.0, 'YB')
	
	For very big numbers that are already logged in the indicated base, use the
	'isexp' flag. I.e. 1000**5.666666666666667 equals 1e+17. 
	>>> byte_units(5.666666666666667, isexp=True) == byte_units(1e+17)
	True
	>>> byte_units(0, isexp=True)
	(1, 'B')
	
	Of course, log values less than 0 are impossible.
	>>> byte_units(-123456789, isexp=True)
	Traceback (most recent call last):
		...
	ValueError: expicit log argument was negative: math domain error
	"""
	if not (base % 10):
		base = 10**3
		prefixes, lprefixes = bytes_by_prefix, log_bytes_by_prefix
	elif not (base % 16): # note that 1000 % 8 == 0
		base = 2**10
		prefixes, lprefixes = ibytes_by_prefix, log_ibytes_by_prefix
	if isexp:
		if size < 0:
			raise ValueError("expicit log argument was negative: math domain error") 
		logsize, pos = size, True
	else:
		if size == 0:
			return 0, lprefixes[0]+'B'
		elif size < 0:
			size, pos = -size, False
		else:
			pos = True
		logsize = log(size, base)
	exp, maxexp = trunc(logsize), len(lprefixes)-1
	exp = min(exp, maxexp)
	m = base**(logsize-exp)
	return m if pos else -m, lprefixes[exp]+'B'
### Much slower method:
#	size = factory(size)
#	for p in prefixes.keys()[:-1]:
#		if size < base: return size, p+'B'
#		else: size /= base
#	return size, prefixes.keys()[-1]+'B'

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
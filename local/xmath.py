from decimal import Decimal
import itertools
from math import *

def split_fraction(n):
	if isinstance(n, Decimal):  return(int(n), n % 1)
	elif isinstance(n, float):  return(int(n), fmod(n, 1.))
	else:					    return(n, 0.)
def sign(n):
	if n == 0:  return 0
	else:		return (1 if n > 0 else -1)
def round_array_to_magnitude(elements, total):
	"""
	Round the elements of an array so that the total sum is closest to total.
	"""
	split_fractions = [ split_fraction(x) for x in elements ]
	whole_sum = float(sum(w for w, f in split_fractions))
	new_sum = whole_sum
	for f in sorted([f for w, f in split_fractions], key=abs, reverse=True):
		if total <= new_sum+sign(f): break
		else: new_sum += sign(f)
	else:
		return [ round(x) for x in elements ]
	fraction_threshold = abs(f)
	return [ w+1 if fraction_threshold < abs(f) else w for w, f in split_fractions ]
#
def weighted_median(values_by_weight, **kwargs):
	n = sum(w for (x, w) in values_by_weight)
	if n % 2: # odd case
		i = (n+1) >> 1
		for (x, f) in sorted(values_by_weight, **kwargs):
			i -= f
			if i <= 0:
				return x
	else:
		x2 = n >> 1
		assert x2
		x1 = x2 - 1
		m1, m2 = itertools.islice(itertools.chain( *((x,)*f for (x,f) in sorted(values_by_weight, **kwargs)) ), x1, x2+1)
		try:
			m = (m1+m2)/2
			return m
		finally:
			return m1, m2
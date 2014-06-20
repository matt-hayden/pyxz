from decimal import Decimal
from math import *

def split_fraction(n):
    if isinstance(n, Decimal):  return(int(n), n % 1)
    elif isinstance(n, float):  return(int(n), fmod(n, 1.))
    else:                       return(n, 0.)
def sign(n):
    if n == 0:  return 0
    else:       return (1 if n > 0 else -1)
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

#!/usr/bin/env python3
import math
from decimal import Decimal, getcontext

def bbp_step(k, *args, one=Decimal(1), two=Decimal(2), four=Decimal(4)):
	return (one/(16**k))*((four/(8*k+1))-(two/(8*k+4))-(one/(8*k+5))-(one/(8*k+6)))
#
def ballard_step(k):
	# (Decimal(-1)**k/(1024**k))*( Decimal(256)/(10*k+1) + Decimal(1)/(10*k+9) - Decimal(64)/(10*k+3) - Decimal(32)/(4*k+1) - Decimal(4)/(10*k+5) - Decimal(4)/(10*k+7) -Decimal(1)/(4*k+3))
def bellard(n):
    pi = Decimal(0)
    k = 0
    while k &lt; n:
        pi += (Decimal(-1)**k/(1024**k))*( Decimal(256)/(10*k+1) + Decimal(1)/(10*k+9) - Decimal(64)/(10*k+3) - Decimal(32)/(4*k+1) - Decimal(4)/(10*k+5) - Decimal(4)/(10*k+7) -Decimal(1)/(4*k+3))
        k += 1
    pi = pi * 1/(2**6)
    return pi

def bbp(n):
	pi = Decimal(0)
	k = 0
	while k < n:
		pi += bbp_step(k)
		k += 1
	return pi
#
getcontext().prec = 10
my_pi = bbp(10)
accuracy = 100*(Decimal(math.pi)-my_pi)/my_pi

print("Pi is approximately " + str(my_pi))
print("Accuracy with math.pi: " + str(accuracy))

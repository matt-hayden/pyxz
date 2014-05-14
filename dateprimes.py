#! /usr/bin/env python
import calendar
from datetime import date
import time

try:
	import primesieve as Primes
except:
	# my 2 GB machine runs out of memory at 220141219 with pyprimes
	import pyprimes as Primes

def pi(*args, **kwargs):
	"""
	Iterator yielding pi(p), p for primes
	"""
	for n, p in enumerate(Primes.primes(*args, **kwargs), start=1):
		yield n, p

today = date.today()
#epoch_now = time.time()
eight_digit_date = int(today.strftime("%Y%m%d"))

start = 19700101
end = 20141231

# day values: 1-31
# month values: 1-12

def is_datestamp(n, years=range(1970, 2037+1), strict=True):
	m, day = divmod(int(n), 100)
	if not 1 <= day <= 31: return False
	m, month = divmod(m, 100)
	if not 1 <= month <= 12: return False
	m, year = divmod(m, 10000)
	if year not in years: return False
	_, days = calendar.monthrange(year, month)
	if days < day: return False
	if (m == 0):
		return n
	elif strict:
		return False
	else:
		return str(n)[-8:]
#
def _checker((n,p), extra_places=2):
	ds = is_datestamp(n, strict=False)
	if ds:
		return (str(ds), str(n), p)
	tp = int(p)
	for i in range(extra_places):
		ds = is_datestamp(tp)
		if ds:
			return (str(ds), str(n), p)
		tp, _ = divmod(tp, 10)
#
if __name__ == '__main__':
	from collections import Counter
	#import multiprocessing.dummy as mp
	import multiprocessing as mp
	import sys
	args = sys.argv[1:]
	stdout, stderr = sys.stdout, sys.stderr
	started = time.clock()
	
	pool = mp.Pool()
	
	#it = pool.map(_checker, pi(stop=20141231)) # 14 s
	#it = pool.map_async(_checker, pi(stop=20141231)).get() # 13.3 s
	#it = pool.imap(_checker, pi(stop=20141231), chunksize=50) # 12.1 s
	#it = pool.imap(_checker, pi(stop=20141231), chunksize=1<<9) # 10.6 s
	#it = pool.imap_unordered(_checker, pi(stop=20141231), chunksize=1<<9) # 10.6 s
	it = pool.imap(_checker, pi(*args), chunksize=1<<9)
	lineno, counter, frequency = 0, 1<<8, Counter()
	for results in it:
		if results:
			lineno += 1
			frequency[results[0]] += 1
			print ' '.join(results)
			#
			if (counter <= lineno):
				sec = time.clock()-started
				print >> stderr, lineno, "found at {:.1f} per second,".format(lineno/sec), len(frequency), "unique"
				counter <<= 2

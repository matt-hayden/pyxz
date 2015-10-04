#! /usr/bin/env python
import calendar
from datetime import date
#import time

import pyprimes as Primes

base = 10

today = date.today()
#epoch_now = time.time()
eight_digit_date = int(today.strftime("%Y%m%d"), base=base)

start = 19700101
end = 20141231

# day values: 1-31
# month values: 1-12

def is_datestamp(n, years=range(1970, 2037+1), strict=True):
	m, day = divmod(n, 100)
	if not 1 <= day <= 31: return False
	m, month = divmod(m, 100)
	if not 1 <= month <= 12: return False
	m, year = divmod(m, 10000)
	if year not in years: return False
	_, days = calendar.monthrange(year, month)
	if days < day: return False
	return (m == 0 if strict else True)
def find_datestamps_within_primes(start, extra_places=4):
	for (n, p) in enumerate(Primes.primes(), start=1):
		if p < start: continue
		tp = p
		for i in range(extra_places):
			if is_datestamp(tp, strict=False): yield (n, p)
			tp, _ = divmod(tp, 10)
			if tp < start: continue
# my 2 GB machine runs out of memory at 220141219
for n, p in find_datestamps_within_primes(start):
	print n, p

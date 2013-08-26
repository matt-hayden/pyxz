from datetime import datetime, timedelta

def mul_timedelta(*args):
	product = 1.0
	for arg in args:
		try:
			sec = arg.total_seconds()
			product *= sec
		except: product *= arg
	return timedelta(seconds=product)

def round_timedelta(td, **kwargs):
	denom = timedelta(**kwargs).total_seconds()
	num = td.total_seconds()
	return timedelta(seconds=denom*round(num/denom))
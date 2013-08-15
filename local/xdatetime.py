from datetime import datetime, timedelta

def round_timedelta(td, **kwargs):
	denom = timedelta(**kwargs).total_seconds()
	num = td.total_seconds()
	return timedelta(seconds=denom*round(num/denom))
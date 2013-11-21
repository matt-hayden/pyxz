from datetime import datetime, timedelta

def mul_timedelta(*args):
	product = 1.0
	for arg in args:
		try:
			sec = arg.total_seconds()
			product *= sec
		except: product *= arg
	return timedelta(seconds=product)
def divmod_timedelta(num, den):
	f, rem = divmod(num.total_seconds(), den.total_seconds())
	return f, timedelta(seconds=rem)
def div_timedelta(num, den):
	return num.total_seconds()/den.total_seconds()

def round_timedelta(td, **kwargs):
	num, denom = td.total_seconds(), timedelta(**kwargs).total_seconds()
    m, rem = divmod(num, denom)
    return timedelta(denom*m if 2*rem < denom else (denom+1)*m)
#
def seconds_from_arg(arg, factory=float):
	"""
	>>> seconds_from_arg(timedelta(seconds=123)) == 123.0
	True

	>>> seconds_from_arg(123.0) == 123.0
	True

	>>> seconds_from_arg('2:03') == 123.0
	True

	>>> seconds_from_arg('01:02:03') == 3723.0
	True
	"""
	try:
		return factory(arg.total_seconds())
	except:
		try:
			return factory(arg)
		except:
			if isinstance(arg, basestring):
				m = re.match(r'((?P<hours>\d+):)?(?P<minutes>\d{1,2}):(?P<seconds>\d\d)', arg)
				if m:
					seconds = 60*60*factory(m.group('hours') or 0)
					seconds += 60*factory(m.group('minutes') or 0)
					seconds += factory(m.group('seconds') or 0)
					return seconds
	raise ValueError("{} not recognized".format(arg))
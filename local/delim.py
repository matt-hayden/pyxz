from local.xcollections import SCounter as Counter
import string

def guess_delimiters(iterable, max_rows=70, exclude=string.letters+string.digits):
	if not hasattr(iterable, 'next'):
		iterable = iter(iterable)
	# equal frequencies of characters:
	delims = set(Counter(next(iterable)).items())
	while max_rows:
		delims &= set(Counter(next(iterable)).items())
		if not delims: return []
		max_rows -= 1
	else:
		return []
	delims = [ (c, n) for (c, n) in delims if c not in exclude ]
	return [ c for c, n in sorted(delims, key=lambda (c, n): n) ]

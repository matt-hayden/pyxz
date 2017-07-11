#!env python
"""
Use this module to extract ManuFlo/Aegis serial numbers from filenames and
text:

>>> aegis_serial_re.search(r'C:\TEMP\L-01234S012.TXT').groups()
('01234S012',)
>>> aegis_serial_searcher.match(r'C:\TEMP\L-01234S012A.TXT').groups()
('01234S012', 'A')
>>> aegis_serial_re.search('0123456789S0123456789').groups()
('56789S012',)
>>> aegis_serial_searcher.match(r'0123456789S0123456789').groups()
Traceback (most recent call last):
  ...
AttributeError: 'NoneType' object has no attribute 'groups'
"""

import os.path
import re

aegis_serial_pattern = '\d{5}[Ss]\d{3}'

## matcher ignores any keycode suffix
aegis_serial_re = re.compile('('+aegis_serial_pattern+')')

## searcher can return a keycode suffix
aegis_serial_searcher = re.compile('(?:.*[^\d])?('+aegis_serial_pattern+')(?P<suffix>[^.\d][^.]*)?.*')

aegis_filename_re = re.compile(r'[^0-9]*'
								'(?P<serial>\d+[Ss]\d{3})'	# serial number
								'(?P<suffix>[a-zA-Z])?'		# someone might tack on a letter
								'.*'
								'(?P<ext>[.][^.]+)+'			# + specifies that only the last .ext is matched. Tricky!
								)

def parse_aegis_serial(text, strict = True):
	"""
	Parse a string for a single serial number
	
	>>> parse_aegis_serial('001234S567.TXT')
	>>> parse_aegis_serial('001234S567.TXT', strict=False)
	'01234S567'
	"""
	dirname, basename = os.path.split(text)
	filepart, ext = os.path.splitext(basename)
	if strict:
		m = aegis_serial_searcher.match(filepart)
	else:
		m = aegis_serial_re.search(filepart)
	if m:
		return m.group(1)
def parse_aegis_serials(texts):
	"""
	Parse a (possibly lengthy) string or iterable for serial numbers on each line.
	"""
	if isinstance(texts, basestring): texts = texts.splitlines()
	return [(parse_aegis_serial(_), _) for _ in texts]

if __name__ == '__main__':
	import doctest
	doctest.testmod()
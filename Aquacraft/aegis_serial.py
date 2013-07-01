#!env python
"""
Use this module to extract ManuFlo/Aegis serial numbers from filenames and
text:

>>> aegis_serial_re.search(r'C:\TEMP\L-01234S012.TXT').groups()
('01234S012',)
>>> aegis_serial_searcher.match(r'C:\TEMP\L-01234S012.TXT').groups()
('01234S012',)
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
aegis_serial_re = re.compile('('+aegis_serial_pattern+')')
aegis_serial_searcher = re.compile('[^\d]*('+aegis_serial_pattern+')[^\d]*')

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
def parse_aegis_serials(text):
	"""
	Parse a (possibly lengthy) string for serial numbers on each line.
	"""
	return [(parse_aegis_serial(_), _) for _ in text.splitlines()]

if __name__ == '__main__':
	import doctest
	doctest.testmod()
#!env python
import os.path
import re

class AegisSerial(dict):
	aegis_serial_re = re.compile(r'(?P<serial>(\d{1,5})[Ss](\d{3}))'	# serial number
								  '(?P<suffix>[^.]*)'					# any suffix added stops with .
								 )
	def from_filename(self, filename, strict=True):
		dirname, basename = os.path.split(filename)
		filepart, ext = os.path.splitext(basename)
		m = self.aegis_serial_re.search(filepart)
		if m: self.update(m.groupdict())
		else: raise ValueError(filename+" not matched")
		if strict: self['serial'] = "{:05d}S{:03d}".format(int(m.groups()[1]), int(m.groups()[2]))
	def __init__(self, *args):
		"""
		>>> print AegisSerial('L-12345S678A.txt.orig')
		12345S678
		
		>>> print AegisSerial(12345,678)
		12345S678
		
		>>> fns = ['Copy of 7638S029A.TXT', r'C:\TEMP\L-07638S147.TXT', '7638S093A.TXT.orig']
		>>> [str(AegisSerial(s)) for s in fns]
		['07638S029', '07638S147', '07638S093']
		"""
		nargs = len(args)
		if nargs == 1:
			self.from_filename(args[0])
		if nargs in (2,3):
			self['serial'] = "{:05d}S{:03d}".format(*args)
	def __str__(self):
		return self['serial']
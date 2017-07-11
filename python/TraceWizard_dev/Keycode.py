from collections import namedtuple
import os.path
import re

class KeycodeError(Exception):
	pass
class KeycodeBase:
	"""(Abstract)
	Subclasses need to implement the following:
	* from_string() sets members from parsing a string
	* format is a format specification specifying only the site info, for example 12X345A2 would format to 12X345
	* extra_format is a format specification rebuilding the string from it's members
	* describe() returns an English string that also uniquely identifies the site (yet not necessarily uniquely identifying the file)
	"""
	def __init__(self, keycode_string, **kwargs):
		self.from_string(keycode_string, **kwargs)
	@property
	def site(self):
		return self.format.format(self)
	def __str__(self):
		return self.extra_format.format(self)
	def __repr__(self):
		return "<{} {!s}: {}>".format(self.__class__.__name__, self, self.describe())
class OldStyleKeycode(KeycodeBase):
	format = "{0.project_count}"
	extra_format = format+"{0.extra}"
	#
	keycode_pattern = re.compile(r'(?P<project_count>\d+)(?P<extra>[^.]*)')
	#
	def from_string(self, keycode_string, **kwargs):
		self.project = kwargs.pop('project', 'project')
		self.filename = keycode_string
		if type(keycode_string) == int:
			self.project_count = keycode_string
		else:
			m = self.keycode_pattern.match(keycode_string)
			if not m:
				raise KeycodeError("'%s' is not an old-style keycode" % keycode_string)
			self.project_count, self.extra = int(m.group('project_count')), m.group('extra').strip()
	def describe(self):
		return "#{:,} in {}".format(self.project_count, self.project)
class NewStyleKeycode(KeycodeBase):
	format = "{0.year2}{0.type_code}{0.year_count}"
	extra_format = format+"{0.extra}"
	type_lookup = { 'A': 'Agricultural',
					'C': 'Commercial',
					'I': 'Industrial',
					'N': 'Institutional',
					'R': 'Residential',
					'S': 'Single-family residential',
					'X': 'Unknown' }
	year2_rollover = 38 # 2038
	#
	keycode_pattern = re.compile(r'(?P<year2>\d{2})(?P<type_code>[a-zA-Z])(?P<year_count>[01]?\d{3})(?P<extra>[^.]*)')
	def describe(self):
		return "{} #{:,} in {}".format(self.site_type, self.year_count, self.year4)
	#
	def from_string(self, keycode_string, **kwargs):
		self.site_type = kwargs.pop('site_type', None)
		self.filename = keycode_string
		if type(keycode_string) == int:
			raise KeycodeError("'%s' is possibly an old-style keycode" % keycode_string)
		m = self.keycode_pattern.match(keycode_string)
		#
		if not m:
			raise KeycodeError("'%s' is not a new-style keycode" % keycode_string)
		self.type_code = m.group('type_code').upper()
		if not self.site_type:
			try:
				self.site_type = self.type_lookup[self.type_code]
			except:
				self.site_type = None
		self.year2, self.year_count = int(m.group('year2')), int(m.group('year_count'))
		self.extra = m.group('extra').strip()
	def has_suffix(self):
		return self.extra not in (None, "")
	@property
	def year4(self):
		assert self.year2 >= 0
		base = 2000 if (self.year2 <= self.year2_rollover) else 1900
		return self.year2+base
	#
	@staticmethod
	def isKeycode(keycode_string):
		try:
			return NewStyleKeycode(keycode_string)
		except:
			return False
class HotKeycode(NewStyleKeycode):
	def from_string(self, *args, **kwargs):
		NewStyleKeycode.from_string(self, *args, **kwargs)
		self.isHot = self.extra.upper().startswith('H')
		if self.isHot:
			self.extra = self.extra[1:]
	def describe(self):
		if not self.isHot:
			return NewStyleKeycode.describe(self)
		else:
			return "{} hot water for #{:,} in {}".format(self.site_type, self.year_count, self.year4)
def Keycode(keycode_string):
	"""
	Convenience function
	"""
	try:
		return HotKeycode(keycode_string)
	except Exception as e:
		return OldStyleKeycode(keycode_string)
	
def splitKeycodeFromPath(filepath, keycoder=Keycode):
	filepath = os.path.normpath(filepath)
	path, filename = os.path.split(filepath)
	filepart, extension = os.path.splitext(filename)
	return path, keycoder(filepart)
if __name__ == '__main__':
	keycoder = Keycode
	for fn in ['12345', '12345.MDB', 'C:\\TEMP\\12345.MDB', 'C:/TEMP/12345.MDB', '/foo/bar/12345.MDB',
			   '12345mh2', '12345mh2.MDB', 'C:\\TEMP\\12345mh2.MDB', 'C:/TEMP/12345mh2.MDB', '/foo/bar/12345mh2.MDB',
			   '12S345', '12S345.MDB', 'C:\\TEMP\\12S345.MDB', 'C:/TEMP/12S345.MDB', '/foo/bar/12S345.MDB',
			   '12S1234', '12S1234.MDB', 'C:\\TEMP\\12S1234.MDB', 'C:/TEMP/12S1234.MDB', '/foo/bar/12S1234.MDB',
			   '12S345H', '12S345H.MDB', 'C:\\TEMP\\12S345H.MDB', 'C:/TEMP/12S345H.MDB', '/foo/bar/12S345H.MDB',
			   '12S345mh2', '12S345mh2.MDB', 'C:\\TEMP\\12S345mh2.MDB', 'C:/TEMP/12S345mh2.MDB', '/foo/bar/12S345mh2.MDB'
			   ]:
		p, k = splitKeycodeFromPath(fn)
		print fn, "=", "{!r}".format(k), "->", k.site
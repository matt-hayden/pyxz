#! env python
from logging import debug, info, warning, error, critical
import os.path
import re

### The 2012 keycode spec: (detects up to 7 characters for the keycode,
### plus a suffix like H,A1,etc.)
keycode_re=re.compile('\s*'
					  '(?P<year_code>\d{2})'
					  '(?P<site_type_code>[a-zA-Z])'
					  '(?P<year_count>\d{3,4})'
					  '(?P<suffix>[a-zA-Z]\w*)?'
					  '\s*')
### Numerical-only format pre-2009:
extra_keycode_res = [re.compile('\s*'
								'(?P<keycode>\d+)'
								'(?P<suffix>[a-zA-Z]\w*)?'
								'\s*'),]
#
keycode_types = { s[0].upper(): s for s in ['Agricultural', 'Commercial', 'Irrigation', 'Multi-family Residential', 'Single-Family Residence']}
keycode_types['N'] = 'Institutional'
keycode_types['X'] = None

### Legacy:
def parse_keycode(t):
	return str(Keycode(t))

def parse_filename(filepath):
	"""
	Convenience function for pulling keycodes from filenames. Some studies used
	integer IDs, others used the 2009 Keycode spec. 
	"""
	if (os.path.sep in filepath) or ('/' in filepath) or (r'\\' in filepath):
		dirname, basename = os.path.split(filepath)
	else:
		basename = filepath
	if os.path.extsep in basename:
		filepart, ext = os.path.splitext(basename)
	else:
		filepart = basename
	id = filepart.upper()
	try:
		id = Keycode(filepart, strict=True)
	except:
		try:
			id = int(filepart[:7])
		except:
			for exp in extra_keycode_res:
				m = exp.match(filepart)
				if m:
					g = m.groupdict()
					if 'keycode' in g:
						id = int(g['keycode'])
	return id
class KeycodeError(Exception):
	pass
class AquacraftSimpleKeycode:
	"""
	The simplest use of unique keycodes follows this pattern:
		YYT(C)CCC
	Example:
		12S345 was assigned in 2012, 'S' is a codeword for Single-family
		residence, and this is the 345 such assignment in that year. Counting
		starts at 1, so 344 keycodes were assigned before this one.
	Note that most earlier code assumes exactly 6 characters in each keycode. 7
	characters are used since around 2012.
	"""
	keycode_re=re.compile('\s*(?P<year_code>\d{2})(?P<site_type_code>[a-zA-Z])(?P<year_count>\d{3,4})(?P<suffix>[a-zA-Z]\w*)?\s*')
	two_digit_max_year=2095
	year_count_max_digits=4
	year_count_max=10**year_count_max_digits-1
	#
	def __init__(self, arg, **kwargs):
		self.from_string(arg, **kwargs)
	@property
	def year(self):
		return self.year4
	def normalized(self, **kwargs):
		assert self.year_count<=self.year_count_max
		if kwargs.pop('keep_suffix', False):
			return "{0.year2}{0.site_type_code}{0.year_count}{0.suffix}".format(self)
		else:
			return "{0.year2}{0.site_type_code}{0.year_count}".format(self)
	def parse(self, text, **kwargs):
		strict = kwargs.pop('strict', True)
		self.text = text
		m=self.keycode_re.match(text)
		if m:
			g = m.groupdict()
			self.suffix = g.pop('suffix',"")
			self.year2, self.site_type_code, self.year_count = int(g['year_code']), g['site_type_code'].upper(), int(g['year_count'])
			#
			self.year4 = 2000+self.year2 if (self.year2 <= self.two_digit_max_year-2000) else 1900+self.year2
			try:
				self.type = keycode_types[self.site_type_code]
			except:
				if strict:
					raise KeycodeError(self.site_type_code, "not a valid type code")
				else:
					self.type = None
		else:
			error_text = "Failed to parse {}".format(text)
			if strict:
				raise KeycodeError(error_text)
			else:
				error(error_text)
	def __str__(self):
		try:
			return self.normalized()
		except:
			return self.text
	def __repr__(self):
		return "<{1} trace {0}>".format(self, self.type or "Unknown")
	def to_tuple(self):
		return self.year2, self.site_type_code, self.year_count, self.suffix
	def __int__(self):
		return int(str(self.year2)+"{1:0{0}d}".format(self.year_count_max_digits, self.year_count))
	def __float__(self):
		return float(self.year2+"."+"{1:0{0}d}".format(self.year_count_max_digits, self.year_count))
	def from_string(self, arg, **kwargs):
		extsep = kwargs.pop('extsep', os.path.extsep)
		self.keep_suffix = kwargs.pop('keep_suffix', True)
		path_warning = kwargs.pop('path_warning', True)
		#
		if isinstance(arg, AquacraftSimpleKeycode):
			text = arg.text
		elif isinstance(arg, basestring):
			text = arg
		else:
			raise KeycodeError(arg)
		if path_warning and ((os.path.sep in text) or ('/' in text) or ('\\' in text)):
			warning("String {} looks like a path, consider os.path.split() and stripext() in this module instead".format(text))
		if extsep and (extsep in text):
			text, ext = os.path.splitext(text)
		self.parse(text, **kwargs)
	def __lt__(self, other):
		if self.type != other.type: raise KeycodeError("Cannot compare {} and {}".format(self,other))
		return (self.to_tuple() < other.to_tuple())
	def __gt__(self, other):
		if self.type != other.type: raise KeycodeError("Cannot compare {} and {}".format(self,other))
		return (self.to_tuple() > other.to_tuple())
	def __hash__(self):
		return int(str(self.year2)
				  +str(ord(self.site_type_code))
				  +"{1:0{0}d}".format(self.year_count_max_digits, self.year_count)
				  +'0')
	def __eq__(self, other):
		if self.type == other.type:
			return (self.year, self.year_count) == (other.year, other.year_count)
		else:
			return False
class AquacraftMultiKeycode(AquacraftSimpleKeycode):
	"""
	Can be subclassed for particular keycode variants in projects. Python
	sets and operators work like so:
	
	>>> Keycode('12X345') == Keycode('12X345')
	True
	>>> Keycode('12X345') == Keycode('12X345abc')
	True
	>>> Keycode('12X345') < Keycode('12X346')
	True
	>>> Keycode('14X345') > Keycode('12X346')
	True
	>>> Keycode('14A345') > Keycode('12X346')
	Traceback (most recent call last):
	KeycodeError: Cannot compare 14A345 and 12X346
	
	Use AquacraftMultiKeycode to allow formal suffixes A1, A2, B1, B2 
	(and so on) to formally differentiate sites:
	>>> AquacraftMultiKeycode('12X345') == AquacraftMultiKeycode('12X345A1')
	False
	
	AquacraftSimpleKeycode has no such logic:
	>>> AquacraftSimpleKeycode('12X345') == AquacraftSimpleKeycode('12X345A1')
	True

	Comparing AquacraftSimpleKeycode and AquacraftMultiKeycode works as
	expected:
	>>> AquacraftMultiKeycode('12S345') == AquacraftSimpleKeycode('12S345')
	True
	>>> AquacraftMultiKeycode('12S345A1') == AquacraftSimpleKeycode('12S345')
	False
	>>> AquacraftMultiKeycode('12S345gal') == AquacraftSimpleKeycode('12S345')
	True
	
	Set logic allows testing if a variation of a keycode is contained in a
	predefined range:
	>>> texts = '12S345 12A345A1 12X345H.twdb 12X345Hre.twdb 12X345gal 12X345CF'.split()
	>>> S = set(AquacraftMultiKeycode(t) for t in texts)
	
	>>> AquacraftMultiKeycode('12S345') in S
	True
	>>> AquacraftSimpleKeycode('12S345') in S
	True
	
	>>> AquacraftMultiKeycode('12S345H') in S
	False
	>>> AquacraftMultiKeycode('12S345H1') in S
	False
	
	Again, AquacraftSimpleKeycode has no suffix logic, which can be useful
	to completely ignore suffix rules:
	>>> AquacraftSimpleKeycode('12S345gal') in S
	True
	>>> AquacraftSimpleKeycode('12S345A1') in S
	True
	
	Note that AquacraftSimpleKeycode and AquacraftMultiKeycode hash differently
	with different suffixes, so, the following operations unintuitively fail:
	>>> AquacraftSimpleKeycode('12A345A1') in S
	False
	
	You have to use:
	>>> AquacraftMultiKeycode('12A345A1') in S
	True
	
	It is correct to say that AquacraftMultiKeycode('12A345') is not in S, so
	neither is AquacraftSimpleKeycode('12A345').
	>>> AquacraftSimpleKeycode('12A345') in S
	False
	"""
	allow_hot=True
	suffix_re=re.compile('\s*[a-zA-Z]\d+\s*')
	#
	def decode_suffix(self, suffix=None):
		p = []
		if not suffix:
			suffix=self.suffix
		if not suffix:
			return []
		suffix=suffix.strip().upper()
		m=self.suffix_re.match(suffix)
		if m:
			p.append('subsite')
		"""
		Modify the logic of this function for human-added filename
		customizations.
		"""
		if self.allow_hot and suffix.startswith('H'):
			p.append('hot')
		if 'RE' in suffix:
			p.append('relog')
		return set(p)
	def normalized(self, **kwargs):
		p = self.decode_suffix()
		if p:
			return AquacraftSimpleKeycode.normalized(self, keep_suffix = True)
		else:
			return AquacraftSimpleKeycode.normalized(self, keep_suffix = False)
	@property
	def isHot(self):
		if self.allow_hot:
			return ('hot' in self.decode_suffix())
		else: return False
	def __eq__(self, other):
		return hash(self) == hash(other)
	def __hash__(self):
		s=self.decode_suffix()
		flags = (4 if 'subsite' in s else 0)+(2 if 'hot' in s else 0)+(1 if 'relog' in s else 0)
		return int(str(self.year2)
				  +str(ord(self.site_type_code))
				  +"{1:0{0}d}".format(self.year_count_max_digits, self.year_count)
				  +str(flags))
def Keycode(*args, **kwargs):
	"""
	Convenience function to generate keycode objects. Can generate ranges,
	unlike AquacraftSimpleKeycode and AquacraftMultiKeycode
	
	Keycode('12X345') returns a single keycode
	Keycode('12X345', 10) returns inclusive keycodes between 345 and 355
	Keycode('12X345', '12X355') returns inclusive keycodes between 345 and 355
	Keycode(12,'X',345) and Keycode(12,'X',345,'H') return one keycode, possibly
	with a suffix.
	"""
	factory=kwargs.pop('factory', AquacraftSimpleKeycode)
	if len(args) == 1:
		return factory(args[0], **kwargs)
	elif len(args) == 2:
		k1 = Keycode(args[0])
		if isinstance(args[1], int):
			assert args[1] != 0
			if args[1] > 0:
				start = k1.year_count
				end = start + args[1] - 1
			elif args[1] < 0:
				end = k1.year_count
				start = end + args[1]
		else:
			k2 = Keycode(args[1])
			end = k2.year_count
		a = []
		for c in range(start, end+1):
			k = Keycode(k1)
			k.year_count = c
			a.append(k)
#		return set(a)
		return a
	elif len(args) >= 3:
		return Keycode(reduce(lambda x,y: x+str(y), [str(a) for a in args]))
#
def splitext(filepath, **kwargs):
	"""
	Behaves like os.path.splitext(), except returning a Keycode where
	appropriate:
	>>> splitext(r'C:/ASDF/12A345suf.CSV')
	('C:/ASDF/12A345suf', '.CSV')
	
	>>> splitext('12A345suf.CSV')
	(<Agricultural trace 12A345>, '.CSV')
	"""
	extsep = kwargs.pop('extsep', os.path.extsep)
	if extsep and (extsep in filepath):
		filepart, ext = os.path.splitext(filepath)
	else:
		filepart, ext = filepath, ''
	try:
		return Keycode(filepart), ext
	except:
		return filepart, ext
#
if __name__=='__main__':
	import doctest
	failures, tests = doctest.testmod()
	if not failures:
		print "doctest.testmod() passed!"
		texts = '12S345 12A345A1 12X345H.twdb 12X345Hre.twdb 12X345gal 12X345CF'.split()
		print "More examples (not checked) from {}".format(' '.join(texts))
		for strict in [True, False]:
			for keep_suffix in [True, False]:
				print "strict: {}, keep_suffix: {}".format(strict, keep_suffix)
				prev = None
				for text in texts:
					try:
						k = AquacraftMultiKeycode(text, strict=strict, keep_suffix=keep_suffix)
						print text, "=", k.to_tuple(), k.decode_suffix(), hash(k)
						if prev:
							print k, "==", prev, ":", (k==prev)
						prev = k
					except Exception as e:
						print text, e
				print
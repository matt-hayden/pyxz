#! env python
"""Since 2009, Aquacraft keycodes are unique identifiers between 6 and 7 
characters long. Before this, identifiers are only unique within certain
studies.

See also: KeycodeTypes, which can identify project and geography by keycode,
and also recognize invalid keycodes.
"""

import collections
from logging import debug, info, warning, error, critical
import os.path
import re

import local.walk

### Numerical-only format pre-2009:
extra_keycode_res = [re.compile('\s*'
								'(?P<keycode>\d+)'
								'(?P<suffix>[a-zA-Z]\w*)?'
								'\s*')]

### Legacy:
def parse_keycode(t):
	return str(Keycode(t))
###

class KeycodeError(Exception):
	pass

def parse_filename(filepath, int_factory=int, strict=False):
	"""
	Convenience function for pulling keycodes from filenames. Some studies used
	integer IDs, others used the 2009 Keycode spec. If an attempt to determine
	Integer ID fails, text is returned.
	"""
#	if (os.path.sep in filepath) or ('/' in filepath) or (r'\\' in filepath):
#		dirname, basename = os.path.split(filepath)
#	else:
#		basename = filepath
	dirname, basename = os.path.split(filepath)
#	if os.path.extsep in basename:
#		filepart, ext = os.path.splitext(basename)
#	else:
#		filepart = basename
	filepart, ext = os.path.splitext(basename)
	try:
		return Keycode(filepart, strict=True)
	except KeycodeError as e:
		if strict: raise e
		else:
			try:
				return int_factory(filepart)
			except:
				for exp in extra_keycode_res:
					m = exp.match(filepart)
					if m:
						g = m.groupdict()
						if 'keycode' in g:
							return int_factory(g['keycode'])
	return filepart.upper()

class AquacraftKeycode(object): # abstract
	AGRICULTURAL	= 'A'
	COMMERCIAL		= 'C'
	IRRIGATION		= 'I'
	MULTIFAMILY		= 'M'
	INSTITUTIONAL	= 'N'
	SINGLEFAMILY	= 'S'
class Aquacraft2YearKeycode(AquacraftKeycode): # abstract
	min_year_for_two_digits, max_year_for_two_digits = 1996, 2095
class AquacraftSimpleKeycode(collections.Hashable, Aquacraft2YearKeycode):
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
	year_count_max_digits=4
	year_count_max=10**year_count_max_digits-1
	
	keycode_re=re.compile('\s*'
						  '(?P<year_code>\d{2})'
						  '(?P<site_type_code>[a-zA-Z])'
						  '(?P<year_count>\d{3,4})'
						  '(?P<suffix>[a-zA-Z]\w*)?'
						  '\s*')
	#
	def __init__(self, arg, **kwargs):
		if isinstance(arg, AquacraftSimpleKeycode):
			self.parse(arg.text, **kwargs)
		else:
			self.from_string(arg, **kwargs)
	@property
	def year(self):
		return self.year4
	def normalized(self, **kwargs):
		assert self.year_count<=self.year_count_max
		if kwargs.pop('keep_suffix', False):
			return "{0.year2:02}{0.site_type_code}{0.year_count:03}{0.suffix}".format(self)
		else:
			return "{0.year2:02}{0.site_type_code}{0.year_count:03}".format(self)
	def parse(self, text, **kwargs):
		strict = kwargs.pop('strict', True)
		self.text = text
		m=self.keycode_re.match(text)
		if m:
			g = m.groupdict()
			self.suffix = g.pop('suffix',"")
			self.year2, self.site_type_code, self.year_count = int(g['year_code']), g['site_type_code'].upper(), int(g['year_count'])
			#
			self.year4 = 2000+self.year2 if (self.year2 <= self.max_year_for_two_digits-2000) else 1900+self.year2
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
	def __repr__(self):	return "<Aquacraft trace {0}>".format(self)
	def to_tuple(self):	return self.year2, self.site_type_code, self.year_count, self.suffix
	def __int__(self):	return int(str(self.year2)+"{1:0{0}d}".format(self.year_count_max_digits, self.year_count))
	def __float__(self):return float(self.year2+"."+"{1:0{0}d}".format(self.year_count_max_digits, self.year_count))
	def from_string(self, text, **kwargs):
		self.keep_suffix = kwargs.pop('keep_suffix', True)
		assert isinstance(text, basestring), KeycodeError(str(text))
		text, ext = os.path.splitext(text)
		self.parse(text, **kwargs)
	def __lt__(self, other):
		other = other if isinstance(other, self.__class__) else Keycode(other)
		if self.site_type_code != other.site_type_code: raise KeycodeError("Cannot compare {} and {}".format(self,other))
		return (self.to_tuple() < other.to_tuple())
	def __gt__(self, other):
		other = other if isinstance(other, self.__class__) else Keycode(other)
		if self.site_type_code != other.site_type_code: raise KeycodeError("Cannot compare {} and {}".format(self,other))
		return (self.to_tuple() > other.to_tuple())
	def __hash__(self):
		return int(str(self.year2)
				  +str(ord(self.site_type_code))
				  +"{1:0{0}d}".format(self.year_count_max_digits, self.year_count)
				  +'0')
	def __eq__(self, other):
		other = other if isinstance(other, self.__class__) else Keycode(other)
		if self.site_type_code == other.site_type_code:
			return (self.year, self.site_type_code, self.year_count) == (other.year, other.site_type_code, other.year_count)
		else:
			return False
class AquacraftMultiKeycode(AquacraftSimpleKeycode):
	"""
	Can be subclassed for particular keycode variants in projects. Python
	sets and operators work like so:
	
	>>> Keycode('12X345') == '12X345'
	True
	>>> Keycode('12X345A1') == '12x345'
	True
	>>> Keycode('12X345') == Keycode('12X345abc')
	True
	>>> Keycode('12X345') < Keycode('12X346')
	True
	>>> Keycode('14X345') > Keycode('12X346')
	True
	>>> Keycode('14A345') > Keycode('12X346')
	Traceback (most recent call last):
		...
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
	allow_hot=True # turn this off to make 'H' nonsignificant at the beginning of the suffix
	suffix_re=re.compile('\s*[a-zA-Z]\d{1,2}\s*') # follow patterns like A2
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
	def __eq__(self, other):
		return hash(self) == hash(other)
	def __hash__(self):
		s=self.decode_suffix()
		# form a bitmask where any alteration of that bitmask distinguishes a site
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
	Keycode('12X345', 10) returns keycodes between 345 and 355 (inclusive)
	Keycode('12X345', '12X355') returns keycodes between 345 and 355 (inclusive)
	Both Keycode(12,AGRICULTURAL,345) and Keycode(12,SINGLEFAMILY,345,'H') each
	return one keycode, possibly with a suffix.
	"""
	factory=kwargs.pop('factory', AquacraftSimpleKeycode)
	if len(args) == 1:
		return factory(args[0], **kwargs)
	elif len(args) == 2:
		k1 = Keycode(args[0])
		if isinstance(args[1], int):
			assert args[1] != 0 # this might become a special case later
			if args[1] > 0:
				start = k1.year_count
				end = start + args[1] - 1
			elif args[1] < 0:
				end = k1.year_count
				start = end + args[1]
		else: # assume it's convertible to a Keycode object
			start = k1.year_count
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
		if Aquacraft2YearKeycode.min_year_for_two_digits <= args[0] <= Aquacraft2YearKeycode.max_year_for_two_digits:
			args[0] %= 100
#		return Keycode(reduce(lambda x,y: x+str(y), [str(a) for a in args]))
		return Keycode(''.join(str(a) for a in args if a is not None))
#
def splitext(filepath, **kwargs):
	"""
	Behaves like os.path.splitext(), except returning a Keycode where
	appropriate:
	>>> splitext(r'C:/ASDF/12A345suf.CSV')
	('C:/ASDF/12A345suf', '.CSV')
	
	>>> splitext('12A345suf.CSV')
	(<Aquacraft trace 12A345>, '.CSV')
	"""
	filepart, ext = os.path.splitext(filepath)
	try:
		return Keycode(filepart), ext
	except:
		return filepart, ext
#
def gen_files_by_keycode(*args, **kwargs):
	"""
	GENERATOR
	
	Input: a list of paths
	Output: pairs of (keycode, [possibly empty list of associated paths])
	"""
	ignore_non_keycodes = kwargs.pop('ignore_non_keycodes', True)
	
	files_by_keycode = collections.defaultdict(list)
	errors = 0
	for f in local.walk.flatwalk(*args):
		try:
			k = parse_filename(f, strict=True)
			files_by_keycode[k].append(f)
		except KeycodeError as e:
			if ignore_non_keycodes: errors += 1
			else: raise e
	info("{} files ignored".format(errors))
	if files_by_keycode:
		for k in Keycode(min(files_by_keycode), max(files_by_keycode)):
			yield k, files_by_keycode[k]
#

def test():
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
#
if __name__=='__main__':
	from collections import Counter
	import sys
	
	import local.console.size
	
	args = sys.argv[1:] or ['.']
	nargs = len(args)
	for arg in args:
		if nargs > 1: print arg+":",
		kfs = list(gen_files_by_keycode(arg))
		if not kfs:
			print "No keycodes recognized"
			continue
		print
		c = Counter(len(fs) for k, fs in kfs)
		width = len(str(max(c)))
		print local.console.size.to_columns(("{:{width}} {:>7}".format(len(fs), k, width=width) for k, fs in kfs), sep="| ")
		print
		width = 12
		print " {:>{width}} {:>{width}} ".format("# keycodes","# files each",width=width)
		print "|{:->{width}}|{:->{width}}|".format("","",width=width)
		for nf, freq in c.items():
			print "|{:>{width}}|{:>{width}}|".format(freq, nf or "(missing)",width=width)
		print "|{:<{width}}|{:<{width}}|".format("total","# files",width=width)
		print "|{:->{width}}|{:->{width}}|".format("","",width=width)
		print "|{:>{width}}|{:>{width}}|".format(sum(c.values()), sum(nk*nf for nf, nk in c.items()),width=width)
		print "|{:_>{width}}|{:_>{width}}|".format("","",width=width)
		print
### EOF
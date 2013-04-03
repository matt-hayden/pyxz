#! env python

import os.path
import re

#
keycode_re=re.compile('\s*(?P<year_code>\d{2})(?P<site_type_code>[a-zA-Z])(?P<year_count>\d{3,4})(?P<suffix>[a-zA-Z]\w*)?\s*')

### Legacy:
def parse_keycode(s, two_digit_year_cutoff=38):
   m=keycode_re.match(s)
   if m:
      g = m.groupdict()
      suffix = g['suffix'] if ('suffix' in g) else ""
      year2, site_type_code, year_count = int(g['year_code']), g['site_type_code'].upper(), int(g['year_count'])
#      year4 = 2000+year2 if (year2 <= two_digit_year_cutoff) else 1900+year2
      return ("{year2}{site_type_code}{year_count}".format(**vars()), suffix)
   else:
      return s
#
keycode_types = { s[0].upper(): s for s in ['Agricultural', 'Commercial', 'Irrigation', 'Multi-family Residential', 'Single-Family Residence']}
keycode_types['N'] = 'Institutional'
keycode_types['X'] = None

class KeycodeError(Exception):
	pass
class AquacraftSimpleKeycode:
	keycode_re=re.compile('\s*(?P<year_code>\d{2})(?P<site_type_code>[a-zA-Z])(?P<year_count>\d{3,4})(?P<suffix>[a-zA-Z]\w*)?\s*')
	two_digit_max_year=2095
	year_count_max_digits=4
	year_count_max=10**year_count_max_digits-1
	#
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
#			self.suffix = g['suffix'] if ('suffix' in g) else ""
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
		elif strict:
			raise KeycodeError("Failed to parse", text)
	def __str__(self):
		return self.normalized()
	def __repr__(self):
		return "<{1} trace {0}>".format(self, self.type or "Unknown")
	def to_tuple(self):
		return self.year2, self.site_type_code, self.year_count, self.suffix
	def __int__(self):
		return int(str(self.year2)+"{1:0{0}d}".format(self.year_count_max_digits, self.year_count))
	def __float__(self):
		return float(self.year2+"."+"{1:0{0}d}".format(self.year_count_max_digits, self.year_count))
	def __init__(self, arg, **kwargs):
		extsep = kwargs.pop('extsep', os.path.extsep)
		self.keep_suffix = kwargs.pop('keep_suffix', True)
		if isinstance(arg, AquacraftSimpleKeycode):
			text = arg.text
		elif isinstance(arg, basestring):
			text = arg
		else:
			raise NotImplementedError(arg)
		if extsep in text:
			text, ext = os.path.splitext(text)
		self.parse(text, **kwargs)
	def __lt__(self, other):
		return (self.to_tuple() < other.to_tuple())
	def __gt__(self, other):
		return (self.to_tuple() > other.to_tuple())
	def __hash__(self):
		return int(str(self.year2)
				  +str(ord(self.site_type_code))
				  +"{1:0{0}d}".format(self.year_count_max_digits, self.year_count)
				  +'0')
class AquacraftMultiKeycode(AquacraftSimpleKeycode):
	allow_hot = True
	suffix_re=re.compile('\s*[a-zA-Z]\d+\s*')
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
		if suffix.startswith('H') and self.allow_hot:
			p.append('hot')
		if 'RE' in suffix:
			p.append('relog')
		return set(p)
	def __eq__(self, other):
		if (self.year, self.site_type_code, self.year_count) == (other.year, other.site_type_code, other.year_count):
			return self.decode_suffix() == other.decode_suffix()
		else:
			return False
	def __hash__(self):
		s=self.decode_suffix()
		flags = (4 if 'subsite' in s else 0)+(2 if 'hot' in s else 0)+(1 if 'relog' in s else 0)
		return int(str(self.year2)
				  +str(ord(self.site_type_code))
				  +"{1:0{0}d}".format(self.year_count_max_digits, self.year_count)
				  +str(flags))
def Keycode(*args, **kwargs):
	"""
	Convenience function to generate keycode objects. 
	"""
	if len(args) == 1:
		return AquacraftSimpleKeycode(args[0], **kwargs)
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
if __name__=='__main__':
	texts = '12S345', '12A345A1', '12X345H.twdb', '12X345Hre.twdb', '12X345gal', '12X345CF'
#	texts += ('12D345','12345')
	print "Testing", texts
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
	S = set([AquacraftMultiKeycode(t) for t in texts])
	print AquacraftMultiKeycode('12S345') in S
	print AquacraftMultiKeycode('12S345H') in S
	print AquacraftMultiKeycode('12S345H1') in S
	print AquacraftMultiKeycode('12S345gal') in S
#
	
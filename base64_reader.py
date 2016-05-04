#! /usr/bin/env python3


import base64
import collections
import hashlib
import logging
import re


logger = logging.getLogger(__name__)
debug, info, warning, error, fatal = logger.debug, logger.info, logger.warning, logger.error, logger.critical

tag_pattern = re.compile('^([-\s]+)(.*(begin|end).*?)([-\s]+)$', re.IGNORECASE)

class Tag(collections.namedtuple('Tag', 'prefix, label, suffix')):
	@staticmethod
	def from_line(arg, ignores=['BEGIN PGP SIGNED MESSAGE']):
		m = tag_pattern.match(arg)
		if m:
			prefix = m.group(1)
			label = m.group(2)
			suffix = m.group(4)
			if label.upper() in ignores:
				return
			if prefix != suffix[::-1]:
				info("Possibly malformed '{}'".format(arg))
			return Tag(prefix, m.group(2), suffix)
	def __str__(self):
		return ''.join(self)
	def __repr__(self):
		return "<{} Tag {}>".format(*self.get_type())
	def get_type(self):
		t1, t2 = [], []
		for w in self.label.split():
			if w.upper() in ('BEGIN', 'END'):
				t1.append(w)
			else:
				t2.append(w)
		return t1, t2
	def is_complement(self, other, boundaries=set('BEGIN END'.split()) ):
		be1, t1 = self.get_type()
		be2, t2 = other.get_type()
		if (t1 != t2): return False
		assert 1 == len(be1) == len(be2)
		return set([ be1[0].upper(), be2[0].upper() ]) == boundaries
class DataSection(collections.namedtuple('DataSection', 'begin, text, end')):
	"""string representation of base64 encoded binary data
	"""
	@staticmethod
	def from_lines(arg):
		begin = arg.pop(0)
		end = arg.pop(-1)
		assert isinstance(begin, Tag)
		assert isinstance(end, Tag)
		return DataSection(begin, arg, end)
	def __str__(self):
		return '\n'.join(str(p) for p in self)
	def __iter__(self):
		yield self.begin
		yield from self.text
		yield self.end
	def __repr__(self):
		_, parts = self.begin.get_type()
		return "<Base64 {} len={:,} B, hash={}>".format(" ".join(parts), len(self.decode()), self.sha256())
	def get_data(self, encoding='latin-1'):
		return b''.join(line.encode(encoding) for line in self.text)
	def decode(self, **kwargs):
		"""Override this
		"""
		return base64.decodebytes(self.get_data(**kwargs))
	def __bool__(self):
		return 0 < len(self.decode())
	def __hash__(self):
		return hash(self.decode())
	def save(self, filename, mode='wb'):
		with open(filename, mode) as fo:
			fo.write(self.decode())
	def sha256(self):
		return hashlib.sha256(self.decode()).hexdigest()
		
class AttribsBeforeEncoding(DataSection):
	@staticmethod
	def from_lines(arg):
		begin = arg.pop(0)
		end = arg.pop(-1)
		assert isinstance(begin, Tag)
		assert isinstance(end, Tag)
		lines, attribs = iter(arg), []
		for line in lines:
			if line.strip():
				attribs.append(line.split(': ', 1))
			else:
				break
		else: # no blank encountered
			lines = arg
		r = DataSection(begin, list(lines), end)
		r.attribs = attribs
		return r
	def __iter__(self):
		yield self.begin
		if self.attribs:
			for k, v in self.attribs:
				yield "{}: {}".format(k, v)
		yield from self.text
		yield self.end
class PgpSection(AttribsBeforeEncoding):
	def __repr__(self):
		_, parts = self.begin.get_type()
		return "<{} len={:,} B, hash={}>".format(" ".join(parts), len(self.decode()), self.sha256())
class RsaSection(AttribsBeforeEncoding):
	def __repr__(self):
		_, parts = self.begin.get_type()
		return "<{} len={:,} B, hash={}>".format(" ".join(parts), len(self.decode()), self.sha256())


class FormatError(Exception):
	pass


def parse(arg, default_factory=DataSection.from_lines):
	if isinstance(arg, str):
		lines = [ line.rstrip() for line in arg.split('\n') ]
	else:
		lines = arg
	plines = [ Tag.from_line(line) or line for line in lines ]
	text_block_by_line, entry_lineno, entry = [], 0, []
	for lineno, line in enumerate(plines, start=1):
		factory = default_factory
		if isinstance(line, Tag):
			if 'PGP' in line.label.upper():
				factory = PgpSection.from_lines
			elif 'RSA PRIVATE KEY' in line.label.upper():
				factory = RsaSection.from_lines
			if entry:
				assert line.is_complement(entry[0])
				entry.append(line)
				yield (entry_lineno, factory(entry))
				entry = []
			else:
				if text_block_by_line:
					yield from text_block_by_line
					text_block_by_line = []
				entry_lineno, entry = lineno, [line]
		elif entry:
			entry.append(line)
		else:
			text_block_by_line.append( (lineno, line) )
	if entry:
		raise FormatError("Mismatched {} section".format(entry[0]))
	if text_block_by_line:
		yield from text_block_by_line


def split(lines, **kwargs):
	nlines, binaries = [], []
	for lineno, part in parse(lines):
		if isinstance(part, DataSection): # part is multiple strings
			try:
				part.decode()
				nlines.append( (lineno, repr(part)) )
				binaries.append(part)
			except Exception as e:
				error("Malformed base64 data: {}".format(e))
				for lineno, line in enumerate(part, start=lineno):
					nlines.append( (lineno, line) )
		else: # part is a string
			nlines.append( (lineno, part) )
	return binaries, nlines


def print_file(filename, number_lines=True):
	with open(filename, 'r') as fi:
		lines = [ line.rstrip() for line in fi ]
	if number_lines:
		spaces = len(str(len(lines)))
		def nprint(*args, **kwargs):
			lineno, args = args[0], args[1:]
			print("{:{}d}".format(lineno, spaces), *args, **kwargs)
	else:
		def nprint(*args, **kwargs):
			args = args[1:]
			print(*args, **kwargs)
	for lineno, part in parse(lines):
		if isinstance(part, DataSection): # part is multiple strings
			try:
				yield part.decode()
				nprint(lineno, repr(part))
				if 2 < len(part):
					nprint(lineno+len(part)-1, '...')
			except Exception as e:
				nprint(lineno, "<Malformed base64 data: {}>".format(e))
				for lineno, line in enumerate(part, start=lineno):
					nprint(lineno, line)
		else: # part is a string
			nprint(lineno, part)
if __name__ == '__main__':
	import sys
	for fn in sys.argv[1:]:
		b = list(print_file(fn))
		if b:
			print()
			print("{} valid".format(len(b)), "binary" if len(b) == 1 else "binaries")

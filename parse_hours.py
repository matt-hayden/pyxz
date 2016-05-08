#! /usr/bin/env python3
import csv
import re

class Comment:
	"""It could be important to implement __len__ on subclasses so that comments are not zero-length"""
	def __init__(self, text=''):
		self.text = text
	def __repr__(self):
		return "{}('{}')".format(self.__class__, self.text)
	def __iter__(self): return iter(self.text)
	def __contains__(self, arg): return (arg in self.text)
class HashComment(Comment):
	pattern = re.compile('^\s*[#]+\s*')
	def __len__(self):
		lt = len(self.text)
		return lt+2 if lt else 1
	def __str__(self):
		if self.text:
			s = self.is_shebang()
			if s:
				return '#! '+s
			else:
				return '# '+self.text
		return '#'
	def __init__(self, arg):
		if isinstance(arg, str):
			self.text = self.pattern.sub('', arg)
		elif hasattr(arg, 'text'):
			self.text = arg.text
		else:
			raise ValueError(arg)
	@staticmethod
	def match(line):
		m = HashComment.pattern.match(line)
		if m:
			return HashComment(line)
	def is_shebang(self):
		if len(self.text) and self.text.startswith('!'):
			return Shebang(self.text[1:].strip())
	def is_vim_modeline(self):
		if len(self.text) and self.text.startswith('vim:'):
			return ModeLine(self.text[4:].strip())
class ModeLine(HashComment):
	def __str__(self):
		if self.text:
			return '# vim: '+self.text
class Shebang(HashComment):
	def __str__(self):
		if self.text:
			return '#! '+self.text
def is_comment(text):
	m = HashComment.match(text)
	if m:
		vl = m.is_vim_modeline()
		if vl: return vl
		return m


def get_send_comments_to(dest):
	assert hasattr(dest, '__call__')
	def co(dest):
		while True:
			n, line = (yield)
			if (n == 0) and isinstance(line, HashComment):
				sb = line.is_shebang()
				if sb: dest( (n, sb) )
			else:
				dest( (n, line) )
	coroutine = co(dest)
	next(coroutine) # coroutine
	return coroutine


def strip_comments(lines, arg=None):
	"Slide comment lines away, optionally to a processing routine or list"
	if hasattr(arg, '__call__'): call = arg
	elif hasattr(arg, 'append'): call = arg.append
	else: raise ValueError(arg)
	for n, line in enumerate(lines):
		if line:
			m = is_comment(line)
			if m:
				call( (n, m) )
			else:
				yield (n, line)


class Parser:
	dialect = 'excel-tab'
	def __init__(self):
		self.comments = []
	def parse(self, filename):
		with open(filename) as fi:
			content = [line.rstrip() for line in fi]
		comment_processor = get_send_comments_to(self.comments.append)
		self.numbered_lines = list(strip_comments(content, comment_processor.send))
	def get_lines(self, with_comments=False):
		if with_comments:
			for n, line in sorted(self.comments+self.numbered_lines):
				yield line
		else:
			for n, line in self.numbered_lines:
				yield line
	@property
	def lines(self):
		return [ str(m) for m in self.get_lines(with_comments=True) ]
	def get_rows(self):
		reader = csv.DictReader(self.get_lines(with_comments=False), dialect=self.dialect)
		yield from reader


p = Parser()
p.parse('hours')
# vim: tabstop=4 shiftwidth=4 softtabstop=4 : number

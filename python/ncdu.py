#! /usr/bin/env python2

from datetime import datetime
import json
import os, os.path

def human_size_1024(si, prefix=['  B', 'kiB', 'MiB', 'GiB', 'TiB']):
	i, de = si, 0
	while (1024 <= i):
		i >>= 10
		de += 1
	if not de:
		return "{} {}".format(i, prefix[0])
	de = min(len(prefix)-1, de)
	return "{:.1f} {}".format(float(si)/(1024**de), prefix[de])
def human_size_1000(si, prefix=[' B', 'kB', 'MB', 'GB', 'TB']):
	i, de = si, 0
	while (1000 <= i):
		i /= 1000
		de += 1
	if not de:
		return "{} {}".format(i, prefix[0])
	de = min(len(prefix)-1, de)
	return "{:.1f} {}".format(float(si)/(1000**de), prefix[de])
def human_size(arg, base=1000):
	if base == 1000:
		return human_size_1000(arg)
	elif base == 1024:
		return human_size_1024(arg)
	else:
		raise ValueError("base={}".format(base))
class NcduEntry:
	def is_error(self):
		return self.attr.get('read_error', None)
	@property
	def name(self):
		try:
			return self.attr['name']
		except:
			return
	def __str__(self):
		return json.dumps(self.get_content(), sort_keys=True)
class NcduFile(NcduEntry):
	def __init__(self, attr):
		self.attr = attr
	def isfile(self):
		return not self.attr.get('notreg', None)
	def islink(self):
		return self.attr.get('hlnkc', None)
	def get_content(self):
		return self.attr
	def __repr__(self):
		return "<file {}>".format(self.name)
	@property
	def size(self):
		return self.attr['asize']
	def get_flags(self):
		flags = ''
		if self.isfile:
			flags += 'f'
		if 0 < self.size:
			flags += 's'
		if self.islink:
			flags += 'h'
class NcduDir(NcduEntry):
	class Totals:
		def __init__(self, arg=(0,0,0,0) ):
			self.ndirs, self.nfiles, self.file_bytes, self.apparent_size = arg
	def __init__(self, arg):
		assert isinstance(arg, (list))
		self.attr = arg.pop(0)
		self.children = []
		a = self.children.append
		for i in arg:
			if isinstance(i, (list, tuple)):
				a(NcduDir(i))
			else:
				a(NcduFile(i))
	def get_content(self):
		return [self.attr]+[ c.get_content() for c in self.children ]
	def walk(self):
		dirs, files = [], []
		for i in self.children:
			if isinstance(i, NcduDir):
				dirs.append(i)
			elif isinstance(i, NcduFile):
				files.append(i)
		dirs_out = [ d.name for d in dirs ]
		yield self.name, dirs_out, files
		for d in dirs:
			if d.name in dirs_out:
				for i in d.walk():
					yield i
	def totalize(self, **kwargs):
		block_size = kwargs.get('block_size', None)
		collapse_hardlinks = kwargs.get('collapse_hardlinks', None)
		if 'finodes' in kwargs:
			finodes = kwargs['finodes']
		else:
			finodes = kwargs['finodes'] = set()
		totals = NcduDir.Totals()
		for i in self.children:
			if isinstance(i, NcduFile):
				totals.nfiles += 1
				if i.isfile():
					ino = i.attr['ino']
					if collapse_hardlinks and (ino in finodes):
						continue
					finodes.add(ino)
					size = i.size
					if block_size:
						fb, rem = divmod(size, block_size)
						totals.apparent_size += fb*block_size
						if rem: totals.apparent_size += block_size
					else:
						totals.apparent_size += size
					totals.file_bytes += size
		parent = kwargs.pop('parent', '')
		if parent is None:
			dirname = kwargs['parent'] = ''
		else:
			dirname = kwargs['parent'] = os.path.join(parent, self.name)
		yield dirname, self.attr, totals
		for i in self.children:
			if isinstance(i, NcduDir):
				for j in i.totalize(**kwargs):
					yield j
	def get_file_size(self, **kwargs):
		g = self.totalize(**kwargs)
		_, _, t = next(g)
		return t.apparent_size
	def get_total_size(self, **kwargs):
		return sum(t.apparent_size for (_, _, t) in self.totalize(**kwargs))
	def print_dirs(self, **kwargs):
		col_width = kwargs.pop('col_width', None)
		key = kwargs.pop('key', None)
		line_format = kwargs.pop('line_format',
		" {:>{col_width[0]}} {:>{col_width[1]}} {:>{col_width[2]}}")
		#rows = list(self.totalize(**kwargs))
		rows = [ (n, a, t) for (n, a, t) in self.totalize(**kwargs)
				 if t.nfiles ]
		if not col_width:
			col_width = (max(len(n) for n, _, _ in rows),
						 1,
						 8)
		if not key:
			def key((n, a, t)):
				return -t.apparent_size
		rows.sort(key=key)
		for n, a, t in rows:
			pn = n[:col_width[0]]
			print line_format.format(n.encode('utf-8'),
				  '',
				  human_size(t.apparent_size),
				  col_width=col_width)
			
class NcduSave(NcduDir):
	def __init__(self, arg, **kwargs):
		if hasattr(arg, 'read'):
			v0, v1, self.attr, entries = json.load(arg, **kwargs)
		else:
			v0, v1, self.attr, entries = arg
		self.children = [NcduDir(entries)]
		self.version = (v0, v1)
	@property
	def root(self):
		assert len(self.children) == 1
		return self.children[0]
	def print_dirs(self, **kwargs):
		kwargs['parent'] = None # without this, full paths are show
		self.root.print_dirs(**kwargs)
	def get_content(self):
		return (self.version[0],
				self.version[1],
				self.attr,
				self.root.get_content())
	@property
	def mtime(self):
		return datetime.fromtimestamp(self.attr['timestamp'])
def open_ncdu(arg, **kwargs):
	if hasattr(arg, 'read'):
		return NcduSave(arg, **kwargs)
	else:
		with open(arg) as fi:
			return NcduSave(fi, **kwargs)
if '__main__' == __name__:
	import sys
	t = open_ncdu(sys.argv[1])
	t.print_dirs()

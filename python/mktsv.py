#! /usr/bin/env python3
import hashlib
import os, os.path
import sys
import urllib.parse

import tqdm

def err(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)


def get_checksum(p, factory=hashlib.md5, progress=None, cache_size=2*1024*2048):
	s = factory()
	if progress:
		def update(c):
			s.update(c)
			progress(len(c))
	else:
		update = s.update
	with open(p, 'rb') as fi:
		c = fi.read(cache_size)
		while len(c):
			update(c)
			c = fi.read(cache_size)
	return s.hexdigest()

def parse_url(arg):
	u = urllib.parse.urlparse(arg, scheme='http')
	if u.scheme.endswith('tp'):
		server, port = u.netloc.rsplit(':', 1)
	_, fn = os.path.split(u.path)
	return fn, u

def make_checksums(urls):
	urls = dict(parse_url(u) for u in urls)
	q, found = dict(urls), []
	for root, dirs, filenames in os.walk('.'):
		dirs = [ d for d in dirs if not d.startswith('.') ]
		filenames = [ f for f in filenames if not f.startswith('.') ]
		for f in filenames:
			if f in q:
				p = os.path.join(root, f)
				stat = os.stat(p)
				found.append( (q.pop(f).geturl(), p, stat.st_size) )
	files_not_found = q
	if files_not_found:
		err("Could not find:")
		err('\n'.join(files_not_found))
	if found:
		total_size = sum(s for u, p, s in found)
		with tqdm.tqdm(total=total_size, unit='B', unit_scale=True, disable=not sys.stderr.isatty()) as bar:
			for u, p, s in found:
				yield u, s, get_checksum(p, progress=bar.update)

###
import sys
with sys.stdin as fi:
	urls = [ line.rstrip() for line in fi ]
if urls:
	print('TsvHttpTransfer-1.0')
	for row in make_checksums(urls):
		print('{}\t{}\t{}'.format(*row))

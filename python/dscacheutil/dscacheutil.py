#!/usr/bin/env python3
from . import *

def dscacheutil(db, *args, **kwargs):
	"""Wrapper for OSX dscacheutil
	Usage: dscacheutil -h
		dscacheutil -q category [-a key value]
		dscacheutil -cachedump [-buckets] [-entries [category]]
		dscacheutil -configuration
		dscacheutil -flushcache
		dscacheutil -statistics
	"""
	if db:
		flags = [ '-q', db ]
	else:
		flags = []
		if not args:
			raise dscacheutilException(__doc__)
	if 'name' in kwargs:
		flags += [ '-a', 'name', kwargs.pop('name') ]
	elif 'ip_address' in kwargs:
		flags += [ '-a', 'ip_address', kwargs.pop('ip_address') ]
	elif 'number' in kwargs:
		flags += [ '-a', 'number', kwargs.pop('number') ]
	elif 'gid' in kwargs:
		flags += [ '-a', 'gid', kwargs.pop('gid') ]
	elif 'port' in kwargs:
		flags += [ '-a', 'port', kwargs.pop('port') ]
	elif 'uid' in kwargs:
		flags += [ '-a', 'uid', kwargs.pop('uid') ]
	if kwargs:
		raise dscacheutilException("{} not supported".format(args))
	proc = subprocess.Popen(['dscacheutil']+flags, stdout=subprocess.PIPE)
	stdout, _ = proc.communicate()
	results = []
	for stanza in stdout.decode('UTF-8').split('\n'*2):
		d = {}
		for line in stanza.splitlines():
			key, value = line.split(':', 1)
			key = key.strip()
			if 'ip_address' == key:
				d['ip_address'] = ipaddress.ip_address(value.strip())
			elif key in ['number', 'gid', 'port', 'uid']:
				d[key] = int(value.strip())
			else:
				d[key] = value.strip()
		if d and d not in results:
			yield d
			results.append(d)

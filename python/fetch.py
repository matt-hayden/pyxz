#! /usr/bin/env python

#import logging
import os, os.path
import subprocess
import sys
import urlparse

try:
	from shlex import quote
except:
	from pipes import quote

#logger = logging.getLogger('' if '__main__' == __name__ else __name__)
#debug, info, warning, error, fatal = logger.debug, logger.info, logger.warning, logger.error, logger.fatal


def fetch(arg, scp_sudo=''):
	""" Return the content of a URI, including scp://
	"""
	if isinstance(arg, (urlparse.ParseResult, urlparse.SplitResult)):
		uri = arg
	else:
		uri = urlparse.urlparse(arg)
	if uri.scheme in ('scp'):
		path = quote(uri.path[1:] if uri.path.startswith('/') else uri.path)
		command = [ 'ssh', uri.netloc ]
		if scp_sudo:
			command.append(scp_sudo)
		command += [ 'cat', path ]
	else:
		command = [ 'curl', uri.netloc ]
	return subprocess.call(command) == 0
def substitute_urls(iterable):
	items = list(iterable)
	for i in range(len(items)-1, 0, -1):
		if '--' == items[i]:
			break
		u = urlparse.urlparse(items[i])
		if u.scheme:
			items[i] = u
		else:
			break
	return items
def parse_args(argv=None):
	if argv is None:
		argv = sys.argv
	mode = argv[1]
	command = substitute_urls(argv[2:])
	labels = [ urlparse.urlunparse(arg) for arg in command if \
			   isinstance(arg, (urlparse.ParseResult, urlparse.SplitResult)) ]
	if not labels:
		return command
	if mode.endswith('diff'):
		pre_command = []
		for t in labels:
			pre_command.extend(['--label', t])
		command = pre_command + command
	elif mode.endswith('grep'):
		command = [ '--label='+t for t in labels ]+command
	else:
		mode = 'fetch'
	return [mode]+command
		
if '__main__' == __name__:
	#logging.basicConfig(level=logging.DEBUG if __debug__ else logging.WARNING)
	#fetch(' '.join(sys.argv[1:]))
	command = []
	for t in parse_args():
		if isinstance(t, (urlparse.ParseResult, urlparse.SplitResult)):
			command.extend(['<(', 'fetch', urlparse.urlunparse(t), ')'])
		else:
			command.append(t)
	print ' '.join(command)

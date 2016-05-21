#! /usr/bin/env python

#import logging
import subprocess
import urllib2


#logger = logging.getLogger('' if '__main__' == __name__ else __name__)
#debug, info, warning, error, fatal = logger.debug, logger.info, logger.warning, logger.error, logger.fatal


def fetch(arg, scp_sudo=''):
	""" Return the content of a URI, including scp://
	"""
	if isinstance(arg, (urllib2.urlparse.ParseResult, urllib2.urlparse.SplitResult)):
		uri = arg
	else:
		uri = urllib2.urlparse.urlparse(arg)
	if uri.scheme in ('scp'):
		path = uri.path[1:] if uri.path.startswith('/') else uri.path
		command = [ 'ssh', uri.netloc ]
		if scp_sudo:
			command.append(scp_sudo)
		command += [ 'cat', path ]
	else:
		command = [ 'curl', uri.netloc ]
	proc = subprocess.Popen(command)
	proc.communicate()
	return proc.returncode == 0

if '__main__' == __name__:
	#logging.basicConfig(level=logging.DEBUG if __debug__ else logging.WARNING)
	import sys
	fetch(' '.join(sys.argv[1:]))

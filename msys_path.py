#!env python
import os.path
import re

msys_absolute_path_re = re.compile(r'[/\\]+(?P<driveletter>[a-zA-Z]):?[/\\](?P<pathpart>.*)')

def windows_path_from_msys(path):
	if path.startswith('//'): # UNC path or Windows switch
		return path
	m = msys_absolute_path_re.match(path)
	if m:
		driveletter, pathpart = m.group('driveletter'), m.group('pathpart')
		return os.path.join(driveletter+':'+os.path.sep, os.path.normpath(pathpart))
	else:
		return os.path.normpath(path)
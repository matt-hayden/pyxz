#!env python
from datetime import datetime
import os.path
import sys

### external module for Windows
from playMP3 import playMP3

# Globals:
dirname=os.path.dirname(sys.argv[0])
quietfiles=[ '.quiet', os.path.expanduser("~/.quiet") ]
soundsdirectories=[ 'sounds/24', 
					os.path.join(dirname, 'sounds/24'), 
					'', 
					os.path.expanduser('~/sounds/24')
					]
tz=None
"""
# To specify a timezone:
from pytz import timezone
tz = timezone('UTC')
"""
#
if __name__=='__main__':
	quiet = False
	for p in quietfiles:
		if os.path.exists(p):
			quiet = True
			break
	if quiet:
		sys.exit(0)
	#
	now=datetime.now(tz)
	soundfilename="%d.mp3" % now.hour
	#
	file_not_found = True
	for p in (os.path.join(d,soundfilename) for d in soundsdirectories):
		if os.path.exists(p):
			file_not_found = False
			break
	if file_not_found:
		sys.exit(1)
	try:
		playMP3(p)
	except:
		sys.exit(-1)
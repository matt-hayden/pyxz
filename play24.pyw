#!env python
from datetime import datetime
import os.path
import sys

from playMP3 import playMP3

try:
	from pytz import timezone
except ImportError:
	print >>sys.stdout, "Python module pytz needed"

def localtime(tz=None):
	return datetime.now(timezone(tz) if tz else None)
#
# Globals:
quietfile=os.path.expanduser("~/.quiet")
soundsdirectory=os.path.expanduser('~/sounds/24')
#
if __name__=='__main__':
	quiet=os.path.exists(quietfile)
	hod=localtime().hour
	soundfilename="%d.mp3" % hod
	soundpath=os.path.abspath(os.path.join(soundsdirectory, soundfilename))
	if not quiet:
		playMP3(soundpath)
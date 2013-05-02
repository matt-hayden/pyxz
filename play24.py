from datetime import datetime
from glob import glob
import os.path
import sys

### external module for Windows
from playMP3 import playMP3

#
soundsdirectories=[ os.path.join("sounds", "24"),
					os.path.expandvars(os.path.expanduser('~/sounds/24')),
					os.path.join(os.path.expandvars('%ProgramFiles%'), "Agent Jack Bauer", "sounds", "24"),
					os.path.join(os.path.expandvars('%ProgramFiles(x86)%'), "Agent Jack Bauer", "sounds", "24")
					]
"""
# To specify a timezone:
from pytz import timezone
tz = timezone('UTC')
"""
tz=None
#
def find_sounds(dirs = soundsdirectories):
	for d in filter(os.path.isdir, dirs):
		if glob(os.path.join(d, "*.mp3")):
			return d
	return None
def get_hourly_soundfile(dir=find_sounds(),
						 now=None
						 ):
	# This is necessary instead of now = datetime.now(tz) above:
	now = now or datetime.now(tz)
	assert os.path.isdir(dir)
	filepath = os.path.join(dir, "{}.mp3".format(now.hour))
	return filepath if os.path.isfile(filepath) else None
#
soundsdir = find_sounds()
def play24():
	soundfile = get_hourly_soundfile(soundsdir)
	assert os.path.isfile(soundfile)
	playMP3(soundfile)
#
if __name__=='__main__':
	play24()
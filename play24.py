from datetime import datetime, timedelta
from glob import glob
import os.path
import sys

### external module for Windows
from playMP3 import playMP3

## To specify a timezone:
#from pytz import timezone
#tz = timezone('UTC')
tz=None

soundsdirectories=[ os.path.join("sounds", "24"),
					os.path.expandvars(os.path.expanduser('~/sounds/24')),
					os.path.join(os.path.expandvars('%ProgramFiles%'), "Agent Jack Bauer", "sounds", "24"),
					os.path.join(os.path.expandvars('%ProgramFiles(x86)%'), "Agent Jack Bauer", "sounds", "24")
					]

def find_sounds(dirs):
	for d in filter(os.path.isdir, dirs):
		if glob(os.path.join(d, "*.mp3")):
			return d
	return None
def get_sounds_lookup(dir=find_sounds(soundsdirectories), strict=False):
	"""
	Returns something like [ "0.mp3", ... , "23.mp3" ]
	"""
	assert os.path.isdir(dir)
	if strict:
		filenames = [ "{}.mp3".format(_) for _ in range(24) ]
		return [ os.path.join(dir, _) for _ in filenames ]
	else:
		soundfiles = glob(os.path.join(dir, "*.mp3"))
		l = len(soundfiles)
		assert l > 0
		if l >= 24:
			return get_sounds_lookup(dir, strict=True)
		elif l >= 12:
			if os.path.join(dir, "12.mp3") in soundfiles:
				filenames = [ "{}.mp3".format(_) for _ in [12]+range(1,12) ]
				return [ os.path.join(dir, _) for _ in filenames ]
		else:
			return [ soundfiles[_ % l] for _ in range(24) ]
#
def play24(now = None, sounds_lookup=get_sounds_lookup(), ahead=timedelta(minutes=5)):
	assert filter(os.path.exists, sounds_lookup)
	if not isinstance(now, datetime):
		if now:
			now = datetime.fromtimestamp(now, tz)
		else:
			now = datetime.now(tz)+ahead
	h = now.hour
	playMP3(sounds_lookup[h])
#
if __name__=='__main__':
	play24()
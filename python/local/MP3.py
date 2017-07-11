# for playback, see: http://www.vb-helper.com/howto_mci_wav.html
# for recording, see: http://www.devx.com/vb2themax/Tip/18383

from ctypes import *
import os.path

winmm = windll.winmm

def mciSend(s):
#	print "Sending", s
	i=winmm.mciSendStringA(s,0,0,0)
	#if i<>0:
	#	print "Error %d in mciSendString %s" % ( i, s )
	if i:
		raise WindowsError(i, "mciSendString failed:", s)

# Copyright (c) 2011 by James K. Lawless
# jimbo@radiks.net http://www.mailsend-online.com
# License: MIT / X11
# See: http://www.mailsend-online.com/license.php
# for full license details.
#def playMP3(mp3Name):
#	### Added to the above:
#	if not os.path.exists(mp3Name):
#		raise IOError(2, "No such file: ", mp3Name)
#	#
#	mciSend("Close All")
#	mciSend("Open \"%s\" Type MPEGVideo Alias theMP3" % mp3Name)
#	mciSend("Play theMP3 Wait")
#	mciSend("Close theMP3")

#playMP3("test.mp3")

def record(filepath, length=None, audio_type="WaveAudio", overwrite=True):
	filepath = os.path.normpath(filepath)
	if os.path.exists(filepath) and not overwrite:
		raise IOError(2, "Refusing to overwrite: ", filepath)
	mciSend("Open New Type {} alias NewRecording".format(audio_type))
	if length:
		mciSend("Set NewRecording time format milliseconds")
		mciSend("Record NewRecording to {} Wait".format(length))
	else:
		mciSend("Record NewRecording")
	mciSend("Save NewRecording {}".format(filepath))
	mciSend("Close NewRecording")
def play(filepath, audio_type=None):
	filepath = os.path.normpath(filepath)
	if not os.path.exists(filepath):
		raise IOError(2, "No such file: ", filepath)
	if not audio_type:
		dirname, basename = os.path.split(filepath)
		filename, ext = os.path.splitext(basename)
		ext = ext.upper()
		if ext == '.MP3':
			audio_type = 'MPEGVideo'
		elif ext == '.WAV':
			audio_type = 'WaveAudio'
		else:
			audio_type = 'MPEGVideo'
	mciSend("Close All")
	mciSend('Open "{}" Type {} Alias PlayFile'.format(filepath, audio_type))
#	mciSend('Open {}!"{}" Alias PlayFile'.format(audio_type, filepath))
	mciSend("Play PlayFile Wait")
	mciSend("Close PlayFile")

if __name__ == '__main__':
	import sys
	for arg in sys.argv[1:]:
		try:
			play(arg)
		except Exception as e:
			print >>sys.stderr, "MP3 failed:", e
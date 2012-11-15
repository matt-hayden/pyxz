# Copyright (c) 2011 by James K. Lawless
# jimbo@radiks.net http://www.mailsend-online.com
# License: MIT / X11
# See: http://www.mailsend-online.com/license.php
# for full license details.

from ctypes import *
import os.path

winmm = windll.winmm

def mciSend(s):
	i=winmm.mciSendStringA(s,0,0,0)
	#if i<>0:
	#	print "Error %d in mciSendString %s" % ( i, s )
	if i:
		raise WindowsError(i, "mciSendString failed:", s)

def playMP3(mp3Name):
	### Added to the above:
	if not os.path.exists(mp3Name):
		raise IOError(2, "No such file: ", mp3Name)
	#
	mciSend("Close All")
	mciSend("Open \"%s\" Type MPEGVideo Alias theMP3" % mp3Name)
	mciSend("Play theMP3 Wait")
	mciSend("Close theMP3")

#playMP3("test.mp3")
#!env python
# -*- coding: latin-1 -*-

### Example calls:
#import win32com.client
#itunes=win32com.client.Dispatch("iTunes.Application")
#itunes.Play()
#itunes.Pause()
#itunes.NextTrack()
#itunes.PreviousTrack()
#itunes.Stop()
### Example track object properties:
# track.Artist
# track.KindAsString	#The encoding
# track.Album
# track.BPM
# track.Composer
# track.Comment
# track.DiscNumber
# track.DiscCount
# track.Enabled
# track.Location
# track.PlayedCount
# track.EQ
# track.Genre
# track.Grouping
# track.Name
# track.Rating	# each star = 20
# track.SkippedCount
# track.TrackNumber
# track.TrackCount
# track.VolumeAdjustment
# track.Year

#import locale
import win32com.client
itunes=win32com.client.Dispatch("iTunes.Application")

def chop(string, length):
	string=string.strip()
	if len(string) <= length:
		return string
	else:
		return (u"%s-%s" %(string[:length-3], string[-2])).encode('utf-8')
def RatingToStars(scalar):
	return scalar/20.0
#
def iTunes_one_line(width=79):
	pl = itunes.CurrentPlaylist
	print pl.Name
	tr = itunes.CurrentTrack
	#locale.setlocale(locale.LC_NUMERIC, 'en_GB')
	summaryelements = [ chop(pl.Name,18),
						chop(tr.Artist,18),
						chop(tr.Name,25),
						"%1.1f Stars" % RatingToStars(tr.Rating) if tr.Rating else "Not Rated",
						"%s/%s" %(tr.Time, tr.Time),
						"%d kb/s" % tr.BitRate,
						"%d kB" %(tr.Size/1000.0)
						]
	return " ".join([ "[%s]" % el for el in summaryelements ])
#del itunes
print iTunes_one_line()
#!env python
from logging import debug, info, warning, error, critical
import logging
logging.basicConfig(level=logging.DEBUG if __debug__ else logging.WARNING)

import glob
import os.path
import re
import sys

from local.sanitize import shell_sanitize
#from local.xcollections import Namespace
from local.xglob import glob
from local.xini import IniParser
from local.xpath import guess_fileset

from local.xcollections import Namespace
class Cut(Namespace): pass

def make_cut_from_frame_sections(section1, section2):
	# returns an object from section1 to section2
	t1, t2 = section1['pkt_pts_time'], section2['pkt_pts_time']
	dur = t2 - t1

class FFMpegIniParser(IniParser):
	# General section
	@property
	def version(self):
		return self.get('General', 'version')
	@property
	def input_name(self):
		return self.get('General', 'ApplyToFile').strip()
	# Info section
	@property
	def output_name(self):
		return self.get('Info', 'SuggestedMovieName').strip()
	# frames sections
	@staticmethod
	def parse_frame_section(lmatch, attribs):
		# lmatch is a string or a regex match
		#tagger = re.compile('frames.frame.(\d+)(.*)')
		#tagger = re.compile('frames([.][^.]+)+')
		if isinstance(lmatch, basestring):
			lmatch = lmatch.split('.')
		elif type(lmatch) is list:
		
		n = int(lmatch.group(1)) if lmatch else None
		child = lmatch.group(2) if lmatch else None
	def get_frame_sections(self, sections=[]):
		section_dict = dict(sections or self.contents())
		unnamer = re.compile('frames.frame.(\d+)(.*)')
		for k, vals in section_dict.iteritems():
			m = unnamer.match(k)
			try:	n = int(m.group(1))
			except:	n = k
			if k.startswith('frames.'):
				if k.endswith('.tags'): continue
				# merge in any separate .tags entries
				if k+'.tags' in section_dict:
					vals.update(section_dict[k+'.tags'])
				else:
					error("{} without {}".format(k, k+'.tags'))
				for k, val in vals.items():
					try:
						v = int(val)
						vals[k] = v
					except:
						try:
							v = float(val)
							vals[k] = v
						except: pass
				yield n, vals
				last_n, last_vals = n, vals
			elif k.startswith('chapters.'):
				has_chapters = True
				for fn, fv in vals.iteritems():
					info("{}: {} = {}".format(k, fn, fv))
	def get_cuts(self, frame_sections=None, min_duration=0):
		cuts = []
		last_n, last_d, last_t = -1, {'pkt_pts_time': 0}, 0
		for n, d in sorted(frame_sections or self.get_frame_sections()):
			debug("Cuts:")
			for fn, fv in d.iteritems():
				debug("{}: {} = {}".format(n, fn, fv))
			t = d['pkt_pts_time']
			dur = t-last_t
			if min_duration <= dur:
				c = Cut(start=last_t, end=t, duration=dur)
				cuts.append((n, c))
				last_t = t
			last_n = n
		return cuts
	def select_cuts(self, criteria, key=None):
		if not key:
			def key((n, d)):
				return d['lavfi.scene_score']
		sections = sorted(self.get_frame_sections(), key=key, reverse=True)
		n = len(sections)
		if type(criteria) is int:
			return self.get_cuts(frame_sections=sections[:criteria], min_duration=5)

def MP4Box_cutter_commands(ffmpeg_ini_filename, input_filename=None, output_pattern=None):
	exe = 'MP4Box.exe' if sys.platform.startswith('win') else 'MP4Box'
	parser = FFMpegIniParser()
	read_files = parser.read(ffmpeg_ini_filename)

	if not input_filename or not os.path.exist(input_filename):
		warning("Guessing movie file from "+ffmpeg_ini_filename)
		fileset = guess_fileset(ffmpeg_ini_filename)
		largest = sorted(fileset, key=os.path.getsize)[-1]
		warning("Guessed "+largest)
		input_filename = largest
	if not output_pattern:
		input_dirname, input_basename = os.path.split(input_filename)
		input_filepart, input_ext = os.path.splitext(input_basename)
		filepart = input_filepart
		# Custom naming:
		if '+' in ffmpeg_ini_filename:
			dirname, basename = os.path.split(ffmpeg_ini_filename)
			filepart, ext = os.path.splitext(basename)
			filepart = 'Scene_'+filepart.split('+',1)[-1]
		#
		ext = '.MP4'
		output_pattern = filepart+'.{}'+ext
	cuts = parser.select_cuts(10)
	assert cuts
	info("{} cuts".format(len(cuts)))
	print "batch <<- EOL"
	for name, cut in cuts:
		output_filename = output_pattern.format(name)
		assert input_filename != output_filename
		assert not os.path.exists(output_filename)
		yield [exe, '-cat', input_filename, '-splitz', '{0.start}:{0.end}'.format(cut), '-new', output_filename]
def MP4Box_cutter(*args, **kwargs):
	for line in MP4Box_cutter_commands(*args, **kwargs):
		print ' '.join(shell_sanitize(t) for t in line)
	print "EOL"
if __name__ == '__main__':
	import sys
	args = sys.argv[1:] or glob('*.INI')
	for arg in args: MP4Box_cutter(arg)
	#testing:
	#parser = FFMpegIniParser()
	#read_files = parser.read(args[0])
	#for section in parser.get_frame_sections():
			#print section


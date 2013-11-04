#!env python
from logging import debug, info, warning, error, critical
import logging
logging.basicConfig(level=logging.DEBUG if __debug__ else logging.WARNING)

from datetime import timedelta
from decimal import Decimal
import json
import os.path

from local.sanitize import shell_sanitize
from local.xglob import glob
from local.xpath import guess_fileset

def scene_key(frame):
	return frame['tags']['lavfi.scene_score']
#
def custom_split_command(video_filename,
				info_filename='',
				frames_filename='',
				output_pattern='',
				average_time_between_chapter_guesses=300):
	"""
	Timestamps are all decimal seconds.
	"""
	ca_filename = video_filename+'.cutlist'
	if os.path.exists(ca_filename):
		raise NotImplementedError("Cut Assistant file {} exists".format(ca_filename))
	basepath, ext = os.path.splitext(video_filename)
	ca_filename = basepath+'.cutlist'
	if os.path.exists(ca_filename):
		raise NotImplementedError("Cut Assistant file {} exists".format(ca_filename))
	#
	info_filename = info_filename or video_filename+'.JSON'
	if not os.path.exists(info_filename):
		basepath, ext = os.path.splitext(video_filename)
		size = os.path.getsize(video_filename)
		info_filename = '{}{}.JSON'.format(size, ext.upper())
	if not os.path.exists(info_filename):
		raise NotImplementedError("No info JSON for {}".format(info_filename))
	info("Using media file description from "+info_filename)
	#
	with open(info_filename) as fi:
		general = json.load(fi, parse_float=Decimal)
	if video_filename.upper() != general['format']['filename'].upper():
		info("Video filename from {} doesn't match {}".format(info_filename, video_filename))
	#if size != int(general['format']['size']):
	#	info("Size from {} doesn't match {}".format(info_filename, video_filename))
	start_time = Decimal(general['format']['start_time'])
	duration = Decimal(general['format']['duration'])
	end_time = start_time+duration
	
	nchapters = len(general['chapters'])
	info("{} chapter(s) specified in {}".format(nchapters or 'No', info_filename)
	#
	if nchapters:
		raise NotImplementedError("No chapter code!")
	else:
		if not frames_filename:
			basepath, ext = os.path.splitext(info_filename)
			frames_filename = basepath+'.frames'+ext
		if os.path.exists(frames_filename):
			info("Using frames from {} to designate chapter marks".format(frames_filename))
			with open(frames_filename) as fi:
				frames_info = json.load(fi, parse_float=Decimal)['frames']
			else:
				frames_info = general['frames']
			frames = sorted(frames_info, key=scene_key, reverse=True)
			nchapters, rem = divmod(duration, average_time_between_chapter_guesses)
			assert nchapters >= 1
			if rem: nchapters += 1
			selected_frames = frames[:int(nchapters)]
			#
			chapters = [ Decimal(f['pkt_pts_time']) for f in selected_frames ]
		else:
			raise NotImplementedError("No frames JSON for {}".format(frames_filename))
	chapters.sort()
	chapters.insert(0, start_time)
	chapters.append(end_time)
	#
	"""
	Output files will have the form input_filename_{}:{}.ext, where {}:{} are the start and end
	in seconds.
	"""
	if not output_pattern:
		dirname, basename = os.path.split(video_filename)
		filepart, ext = os.path.splitext(basename)
		if ext.upper() not in ('.MP4'):
			warning("{} not a MP4 container".format(video_filename))
			ext = '.MP4'
		output_pattern = filepart+'_{}'+ext
	def output_namer(*args):
		return output_pattern.format('_'.join(str(a) for a in args))
	#
	###
	cuts = zip(chapters, chapters[1:])
	output_names = [ output_namer(int(p[0]), int(p[-1])) for p in cuts ]
	assert video_filename not in output_names
	#
	exe = 'MP4Box'
	commands = []
	y = commands.append
	for (start, end), fn in zip(cuts, output_names):
		y([exe, video_filename, '-splitz', '{}:{}'.format(start, end), '-new', '-out', fn ])
	#for line in commands:
	#	print ' '.join(shell_sanitize(t) for t in line)
	return commands
#

def create_split_command(filename, frames_filename='', video_filename='', average_time_between_splits=300, output_pattern = ''):
	with open(filename) as fi:
		general = json.load(fi, parse_float=Decimal)
	video_filename = video_filename or general['format']['filename']
	start_time = Decimal(general['format']['start_time'])
	duration = Decimal(general['format']['duration'])
	end_time = start_time+duration
	size = int(general['format']['size'])
	#
	if not os.path.exists(video_filename):
		fs = list(guess_fileset(filename))
		fs.sort(key=os.path.getsize)
		largest = fs[-1]
		video_filename = largest
	if not frames_filename:
		basepath, ext = os.path.splitext(filename)
		frames_filename = basepath+'.frames'+ext 
	if not output_pattern:
		dirname, basename = os.path.split(video_filename)
		filepart, ext = os.path.splitext(basename)
		if ext.upper() not in ('.MP4'):
			warning("{} not a MP4 container".format(video_filename))
			ext = '.MP4'
		output_pattern = filepart+'_{}'+ext
	def output_namer(*args):
		return output_pattern.format('_'.join(str(a) for a in args))
	#
	if os.path.exists(frames_filename):
		with open(frames_filename) as fi:
			frames_info = json.load(fi, parse_float=Decimal)
	else:
		frames_info = general['frames']
	#
	frames = sorted(frames_info, key=scene_key, reverse=True)
	nselected, rem = divmod(duration, average_time_between_splits)
	assert nselected >= 1
	if rem: nselected += 1
	selected_frames = frames[:int(nselected)]
	#
	cuttimes = [ Decimal(f['pkt_pts_time']) for f in selected_frames ]
	cuttimes.sort()
	cuttimes.insert(0, start_time)
	cuttimes.append(end_time)
	cuts = zip(cuttimes, cuttimes[1:])
	output_names = [ output_namer(int(p[0]), int(p[-1])) for p in cuts ]
	assert video_filename not in output_names
	#
	exe = 'MP4Box'
	commands = []
	y = commands.append
	for (start, end), fn in zip(cuts, output_names):
		y([exe, video_filename, '-splitz', '{}:{}'.format(start, end), '-new', '-out', fn ])
	#for line in commands:
	#	print ' '.join(shell_sanitize(t) for t in line)
	return commands
#
if __name__ == '__main__':
	import sys
	args = sys.argv[1:] or glob('*.avi', '*.mov', '*.mp4')
	for arg in args:
		for line in custom_split_command(arg):
			print ' '.join(shell_sanitize(t) for t in line)
			print

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

if __name__ == '__main__':
	import sys
	args = sys.argv[1:] or glob('*.JSON')

	average_time_between_splits = 200
	output_pattern = ''
	"""
	Timestamps are all decimal seconds.
	"""
	for fni in args:
		with open(fni) as fi:
			p = json.load(fi, parse_float=Decimal)
		input_filename = p['format']['filename']
		if not os.path.exists(input_filename):
			fs = guess_fileset(fni)
			fs.sort(key=os.path.getsize)
			largest = fs[-1]
			input_filename = largest
		if not output_pattern:
			dirname, basename = os.path.split(input_filename)
			filepart, ext = os.path.splitext(basename)
			if ext.upper() not in ('.MP4'):
				warning("{} not a MP4 container".format(input_filename))
				ext = '.MP4'
			output_pattern = filepart+'_{}'+ext
		def output_namer(*args):
			return output_pattern.format('_'.join(str(a) for a in args))
		start_time = Decimal(p['format']['start_time'])
		duration = Decimal(p['format']['duration'])
		end_time = start_time+duration
		size = int(p['format']['size'])
		frames = sorted(p['frames'], key=scene_key, reverse=True)
		#
		nselected, rem = divmod(duration, average_time_between_splits)
		assert nselected >= 1
		if rem: nselected += 1
		selected_frames = frames[:int(nselected)]
		selected_frames.sort(key=lambda f: f['pkt_pts_time'])
		#
		cuttimes = [ Decimal(f['pkt_pts_time']) for f in selected_frames ]
		cuttimes.insert(0, start_time)
		cuttimes.append(end_time)
		cuts = zip(cuttimes, cuttimes[1:])
		output_names = [ output_namer(int(p[0]), int(p[-1])) for p in cuts ]
		assert input_filename not in output_names
		#
		exe = 'MP4Box'
		commands = []
		for (start, end), fn in zip(cuts, output_names):
			commands.append([exe, input_filename, '-splitz', '{}:{}'.format(start, end), '-new', '-out', fn ])
		for line in commands:
			print ' '.join(shell_sanitize(t) for t in line)

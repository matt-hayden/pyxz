#!env python
import ConfigParser
import glob
import os.path
import sys

from local.sanitize import shell_sanitize
from local.xcollections import Namespace
from local.xglob import glob
from local.xpath import guess_fileset

def guess_input_filename(cutlist_filename, exclude_files=glob('*.bak', '*.cutlist')):
	poss = guess_fileset(cutlist_filename, exclude_files=exclude_files)
	largest = sorted(poss, key=os.path.getsize)[-1]
	return largest

class Cut(Namespace):
	@property
	def end(self):
		return self.start+self.duration
	def to_MP4Box_split(self):
		return '{}:{}'.format(self.start, self.end)

class CutListParser(ConfigParser.SafeConfigParser):
	cut_factory = Cut
	@property
	def version(self):
		return self.get('General', 'version')
	@property
	def input_name(self):
		return self.get('General', 'ApplyToFile').strip()
	@property
	def output_name(self):
		return self.get('Info', 'SuggestedMovieName').strip()
	@property
	def cut_sections(self):
		sections = [ s for s in self.sections() if s.startswith('Cut') ]
		return sections
	@property
	def cuts(self):
		return [ (section, self.cut_factory(start=self.getfloat(section, 'Start'), duration=self.getfloat(section, 'Duration'))) for section in self.cut_sections ]

def MP4Box_cutter_commands(cutlist_filename, input_filename=None, output_pattern=None):
	exe = 'MP4Box.exe' if sys.platform.startswith('win') else 'MP4Box'
	parser = CutListParser()
	read_files = parser.read(cutlist_filename)

	if not input_filename or not os.path.exist(input_filename):
		input_filename = guess_input_filename(cutlist_filename)
	if not output_pattern:
		input_dirname, input_basename = os.path.split(input_filename)
		input_filepart, input_ext = os.path.splitext(input_basename)
		filepart = input_filepart
		# Custom naming:
		if '+' in cutlist_filename:
			dirname, basename = os.path.split(cutlist_filename)
			filepart, ext = os.path.splitext(basename)
			filepart = 'Scene_'+filepart.split('+',1)[-1]
		#
		ext = '.MP4'
		output_pattern = filepart+'.{}'+ext
	for name, cut in parser.cuts:
		output_filename = output_pattern.format(name)
		assert input_filename != output_filename
		assert not os.path.exists(output_filename)
		yield [exe, '-cat', input_filename, '-split-chunk', cut.to_MP4Box_split(), '-new', output_filename]
def MP4Box_cutter(*args, **kwargs):
	for line in MP4Box_cutter_commands(*args, **kwargs):
		print ' '.join(shell_sanitize(t) for t in line)
if __name__ == '__main__':
	import sys
	args = sys.argv[1:] or glob('*.cutlist')
	for arg in args: MP4Box_cutter(arg)

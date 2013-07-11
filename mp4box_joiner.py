#!env python
from collections import Counter
import os.path
from subprocess import *

from local.flatten import flatten

def find_mp4box_executable(paths = []):
	if not paths:
		programfiles = os.path.expandvars('%ProgramFiles%')
		search_files = [ 'GPAC*\\MP4Box.exe',
						 'MeGUI*\\tools\\mp4box\\MP4Box.exe',
						 'MP4Box*\\MP4Box.exe',
						 'StaxRip*\\Applications\\MP4Box\\MP4Box.exe' ]
		paths = [os.path.join(programfiles, _) for _ in search_files]
	latest = []
	for f in glob(paths):
		if os.path.exists(f):
			try:
	#			mp4box_version = [ _ for _ in check_output((f, '-version')).splitlines() if _ ]
				mp4box_version = check_output((f, '-version')).splitlines()[0]
			except CalledProcessError as e:
				continue
			if latest < [mp4box_version, f]:
				latest = [mp4box_version, f]
	return latest[-1]
def my_commonprefix(args, **kwargs):
	prefix = os.path.commonprefix(args, **kwargs)
	if prefix:
		ii = len(prefix)
	while all([_[ii-1].isdigit() for _ in args]):
		ii -= 1
	return prefix[:ii]
def get_output_filename(args, sep='_'):
	dirnames, basenames = zip(*[os.path.split(_) for _ in args])
	fileparts, extensions = zip(*[os.path.splitext(_) for _ in basenames])
	c = Counter(_.upper() for _ in extensions)
	extension, _ = c.most_common(1)[0]
	prefix = my_commonprefix(list(_.lower() for _ in fileparts))
	if prefix:
		ii = len(prefix)
		iparts = [_[ii:] for _ in fileparts]
		return prefix+sep.join(iparts)+extension
	else: return 'joined'+extension
def get_join_syntax(args,
					fileout = ''):
	mp4box_args = [('-cat', _) for _ in args]
	mp4box_args.append(fileout or get_output_filename(args))
	return list(flatten(mp4box_args))
if __name__=='__main__':
	import sys
	
	mp4box_executable = find_mp4box_executable()
	args = sys.argv[1:]
	
	s = get_join_syntax(args)
	print mp4box_executable, s
#	mp4box_version = check_output((mp4box_executable, '-version')).splitlines()
#	print mp4box_version
	join_results = call(flatten((mp4box_executable, s)))
	if join_results: # are not 0
		print "ERROR", join_results
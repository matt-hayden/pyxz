#!env python
from collections import Counter
import os.path

from flatten import flatten

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
	from subprocess import *
	import sys
	mp4box_executable = os.path.expandvars(r'%PROGRAMFILES%\MP4Box-0.4.6-dev_20091013\MP4Box.exe')
	s = get_join_syntax(sys.argv[1:])
	print mp4box_executable, s
	mp4box_version = check_output((mp4box_executable, '-version')).splitlines()
	print mp4box_version
	join_results = call(flatten((mp4box_executable, s)))
	if join_results: # are not 0
		print "ERROR", join_results
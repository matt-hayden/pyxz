#!env python
from collections import Counter
import os.path

from local.xcollections import is_range
from av_split_join import *

def my_commonprefix(args, **kwargs):
	"""
	Remove all digits from the end of a commonprefix.
	"""
	prefix = os.path.commonprefix(args, **kwargs)
	if prefix:
		ii = len(prefix)
#	while all([_[ii-1].isdigit() for _ in args]):
	while prefix[ii-1].isdigit():
		ii -= 1
	return prefix[:ii]
def get_output_filename(args, sep='_'):
	"""
	Jam a bunch of numerical suffixes into the end of a commonprefix.
	"""
	dirnames, basenames = zip(*[os.path.split(_) for _ in args])
	fileparts, extensions = zip(*[os.path.splitext(_) for _ in basenames])
	c = Counter(_.upper() for _ in extensions)
	extension, _ = c.most_common(1)[0]
	prefix = my_commonprefix(list(_.lower() for _ in fileparts))
	if prefix:
		ii = len(prefix)
		iparts = [_[ii:] for _ in fileparts]
		if is_range(iparts):
			return prefix+sep+'{}-{}'.format(iparts[0], iparts[-1])+extension
		else:
			return prefix+sep.join(iparts)+extension
	else: return 'joined'+extension
def _get_join_parts(args, fileout):
	exts = set(os.path.splitext(_).upper() for _ in args)
	if exts & set(['.ASF', '.WMA', '.WMV']):
		return find_asfbin_executable(), asfbin_join_syntax(args, fileout)
#	elif exts == set(['.MKV']):
#		return find_mkvmerge_executable(), mkvmerge_join_syntax(args, fileout)
	elif exts & set(['.MPG', '.MPEG', '.MP4', '.M4V']):
		return find_mp4box_executable(), mp4box_join_syntax(args, fileout)
	else:
		raise NotImplementedError("Please edit av_join.py to support {} containers".format(exts))
def join(args, fileout=None):
	if fileout is None: fileout = get_output_filename(args)
	exe, exe_args = _get_join_parts(args, fileout)
	join_results = call([exe]+exe_args)
	if join_results: # are non-zero
		raise Exception(join_results)
#
if __name__=='__main__':
	import sys
	args = sys.argv[1:]
	join(args)
from itertools import groupby
import os
import os.path

def commondir(paths, seps=r'/\\+'):
	"""
	Like os.path.commonprefix, except only a full path is returned, including
	empty.
	"""
	prefix = os.path.commonprefix(paths)
	while prefix and prefix[-1:] not in seps:
		prefix = prefix[:-1]
	return prefix
def find_repositories(root, stopfiles=['.git']):
	"""
	GENERATOR
	Top-down search of a directory hierarchy, stopping at the first match of a
	particular file. Multiple directories may be returned, and some
	repositories may be missed if nested under different repositories.
	"""
	stopfileset = set(_.lower() for _ in stopfiles)
	for parent, dirs, files in os.walk(root):
		collisions = stopfileset & set(_.lower() for _ in dirs)
		if collisions:
			dirs = [] # stop for this tree
			for stopfile in collisions:
				yield os.path.join(parent, stopfile)
		collisions = stopfileset & set(_.lower() for _ in files)
		if collisions:
			dirs = [] # stop for this tree
			for stopfile in collisions:
				yield os.path.join(parent, stopfile)
def walklist(filenames,
			 check_for_dirs=True,
			 root=''):
	"""
	GENERATOR
	Input: a list of filenames
	Arguments:
		check_for_dirs	When presented with an entry, check to see if it's a
						directory. check_for_dirs=False implies all such
						entries are returned in the 'files' member.
		root			If 'check_for_dirs' and not running in the same
						directory, specify root.
	Output: a walk()-like structure:
		[ (root, dirs, files), ... ]
	Exact fidelity to the same results as walk() is not guaranteed.
	"""
	found_dirs, sfilenames = [], []
	if check_for_dirs:
		for path in filenames:
			if os.path.isdir(os.path.join(root, path)):
				found_dirs.append(os.path.split(path))
			else:
				sfilenames.append(os.path.split(path))
		found_dirs.sort()
	else:
		sfilenames = [os.path.split(_) for _ in filenames]
	sfilenames.sort()
	for dirname, g in groupby(sfilenames, key=lambda _:_[0]):
		if dirname in found_dirs:
			found_dirs.remove(dirname)
		yield dirname, [], [_[-1] for _ in g]
	if found_dirs:
		yield '', found_dirs, [] # lastly, directories not matching any files
###
### Legacy:
gen_rdf_from_list=walklist
###
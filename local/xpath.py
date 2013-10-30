import os.path
import re

from xglob import glob

def separate_paths_at_component(paths, component='', splitter=None):
	seps = set()
	#
	if component:
		splitter = re.compile(r'(?:\\|\A)('+component+r')(?:\\|\Z)', re.IGNORECASE)
	for haystack in paths:
		s = [x for x in splitter.split(haystack, 1) if x]
		seps.add(tuple(s))
	return seps
def parents(pathspec):
	seen = []
	root, basename = os.path.abspath(pathspec), '.'
	while basename and (root not in seen):
		seen.append(root)
		root, basename = os.path.split(root)
	return seen
def find_repository_top(cwd=os.getcwd(), stopnames=['.git']):
#	stopnames = set(_.lower() for _ in stopnames)
	for root in parents(cwd):
		for stopname in stopnames:
			if os.path.exists(os.path.join(root, stopname)): return root
#
def guess_fileset(filename, exclude_files=[], include_pattern='*'):
	exclude_files = set(exclude_files)
	exclude_files.add(filename)
	basepath, ext = os.path.splitext(filename)
	poss = set(glob(basepath+include_pattern))
	poss -= exclude_files
	while basepath and not poss:
		for sep in ['+', ' ', '.', '_']:
			if sep in basepath:
				basepath, ext2 = basepath.rsplit(sep, 1)
				ext = ext2+ext
				break
		poss = set(glob(basepath+'*'))
		poss -= exclude_files
	return poss or filename
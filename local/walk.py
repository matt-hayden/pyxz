from itertools import groupby
import os.path

def gen_rdf_from_list(filenames, check_for_dirs=True):
	"""
	Input: a list of filenames
	Output: a walk()-like structure:
		[ (root, dirs, files), ... ]
	Exact fidelity to the same results as walk() is not guaranteed.
	"""
	found_dirs, sfilenames = [], []
	if check_for_dirs:
		for path in filenames:
			if os.path.isdir(path):
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
		yield '', found_dirs, [] # directories not matching any files
from datetime import datetime
from itertools import groupby, izip
import os
import os.path
import stat
import re

from flatten import flatten

def get_stat_type(mode, like_ls=False):
	if not isinstance(mode, int):
		mode = mode.st_mode
	if stat.S_ISDIR(mode):		return 'd'
	elif stat.S_ISCHR(mode):	return 'c'
	elif stat.S_ISBLK(mode):	return 'b'
	elif stat.S_ISREG(mode):	return '-'
	elif stat.S_ISFIFO(mode):	return 'p'
	elif stat.S_ISLNK(mode):	return 'l'
	elif stat.S_ISSOCK(mode):	return 's'
	else:						return '?' if like_ls else 'U'
def findutils_printf_lookup_term1(token, mystat, time_converter=datetime.fromtimestamp):
	"""
	These are all accessible (but not necessarily meaningful) in Windows
	"""
	if token == '%a':		return time_converter(mystat.st_atime)
	elif token == '%c':		return time_converter(mystat.st_ctime)
	elif token == '%D':		return mystat.st_dev
	elif token == '%G':		return mystat.st_gid
	elif token == '%i':		return mystat.st_ino
	elif token == '%m':		return [int(c) for c in '{:o}'.format(mystat.st_mode)]
	elif token == '%#m':	return [int(c) for c in '{:04o}'.format(mystat.st_mode)]
	elif token == '%n':		return mystat.st_nlink
	elif token == '%s':		return mystat.st_size
	elif token == '%t':		return time_converter(mystat.st_mtime)
	elif token == '%U':		return mystat.st_uid
	elif token == '%y':		return get_stat_type(mystat.st_mode)
	else:					return token
def walk_printf(parent,
				printf_spec,
				printf_splitter=re.compile('(?<!%)(%[a-zA-Z]|%#m)'),
				allow_file_args=True,
				no_join=False):
	"""
	GENERATOR
	Input:
		Starting directory
		spec expected by find -printf
	Output:
		(root, results), (dir, result)..., (file, result)...
		
	The spec could be of the form '%P\t%s\n', for instance. Calling with
	'%P %s'.split() would result in the unsplit version of '%P%s', or '%P%s'
	with the no_join = True argument. Not all GNU findutils tokens are 
	supported, and (at least on Windows) some values from stat are meaningless.
	
	Arguments:
		printf_splitter		has a .split() method that would divide the spec
		allow_file_args		normally, os.walk would return nothing if the
							given parent is just a file (instead of a 
							directory) allow_file_args=False simulates that
							behaviour.
		no_join				False (the default) returns a string
							True returns a tuple of parsed values
	"""
	if isinstance(printf_spec, basestring):
		terms = [token for token in printf_splitter.split(printf_spec) if token != ''] # bug in splitting on the above regex: empty matches exist between matches of (%[a-zA-Z]|%#m)
	else:
		terms = [str(t) for t in flatten(printf_spec)]
		no_join = True
	def findutils_printf_lookup_term2(token, root, subpath):
		"""
		These are all accessible in Windows
		"""
		if token == '%f':		return subpath
		elif token == '%h':		return '.' if root == '' else root
		elif token == '%P':		return os.path.join(root, subpath)
		elif token == '%p':		return os.path.join(parent, root, subpath)
		else:					return token
	def findutils_printf_lookup(root, subpath, myterms=terms[:]):
		myterms = [findutils_printf_lookup_term2(token, root, subpath) for token in myterms]
		myterms = [findutils_printf_lookup_term1(token, os.stat(os.path.join(root, subpath))) for token in myterms]
		return myterms
	if os.path.isdir(parent):
		for root, dirs, files in os.walk(parent):
			# could exclude dirs here
			rootp	= findutils_printf_lookup('', root)
			dirsp	= (findutils_printf_lookup(root, d) for d in dirs)
			filesp	= (findutils_printf_lookup(root, f) for f in files)
			if not no_join:
				rootp	= ''.join(str(p) for p in rootp)
				dirsp	= (''.join(str(p) for p in flatten(sp)) for sp in dirsp)
				filesp	= (''.join(str(p) for p in flatten(sp)) for sp in filesp)
			yield (root, rootp), izip(dirs, dirsp), izip(files, filesp)
	elif allow_file_args:
		parentp	= findutils_printf_lookup('', parentp)
		if not no_join:
			parentp = ''.join(str(p) for p in flatten(parentp))
		yield '', [], [(parent, parentp)]
	else:
		yield '', [], []
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
#
def separate_paths_at_component(paths, component='', splitter=None):
	seps = set()
	#
	if component:
		splitter = re.compile(r'(?:\\|\A)('+component+r')(?:\\|\Z)', re.IGNORECASE)
	for haystack in paths:
		s = [x for x in splitter.split(haystack, 1) if x]
		seps.add(tuple(s))
	return seps
#
def flatwalk(*args, **kwargs):
	"""
	A non-generator walk function combining files from each argument.
	
	Input: a list of paths
	Output: a set of unique paths
	"""
	file_args_are_lists = kwargs.pop('file_args_are_lists', False)
	filenames = set()
	for arg in args:
		if os.path.isfile(arg):
			if file_args_are_lists: g = local.walk.walklist(arg)
			else: filenames.add(arg)
		elif os.path.isdir(arg): g = os.walk(arg)
		elif not os.path.exists(arg): raise Exception(arg+" not found")
		# else: # special file?
		for root, dirs, files in g:
			filenames.update(os.path.join(root, f) for f in files)
	return filenames
### Legacy:
gen_rdf_from_list=walklist
###

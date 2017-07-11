#! /usr/bin/env python2
from collections import Counter
import os
import os.path
from zipfile import ZipFile

from psutil import Popen
from winshell import delete_file, x_winshell as WinShellException

from local.walk import walklist

UNZIP=['unzip.exe','-C','-s']

def get_zipdirs(filename):
	with ZipFile(filename) as zfi:
		return [root for root, dirs, files in walklist(zfi.namelist(), check_for_dirs=False)]
#
def unzipper(zipfilename, cwd='', junk_paths=1, into_own_directory=True, overwrite=False):
	zipfilepath = os.path.join(cwd, zipfilename)
	inside_dirs = get_zipdirs(zipfilepath)
	#
	dirname, basename = os.path.split(zipfilepath)
	filepart, ext = os.path.splitext(basename)
	#
	if into_own_directory is None:
		for subdir in inside_dirs:
			if not os.path.commonprefix(filepart, subdir):
				into_own_directory = True
				break
		else: into_own_directory = False
	#
	dest = os.path.join(dirname, filepart)
	if into_own_directory and os.path.exists(dest):
		if os.path.isdir(dest):
			assert not overwrite, "{} exists".format(dest)
		else:
			assert not overwrite, "File {} exists!".format(dest)
	#
	ndirs = len(inside_dirs)
	if ndirs == 0:
		raise IOError(zipfilepath+" has no members!")
	elif ndirs == 1: many_paths = False
	else: many_paths = True
	if junk_paths == 1: junk_paths = not many_paths
	myargs = UNZIP[:]
	if junk_paths: myargs.append('-j')
	if into_own_directory:
#		dirname = os.path.splitext(zipfilename)[0]
#		myroot = os.path.join(cwd, dirname)
#		if os.path.isdir(myroot):		raise IOError(myroot+" exists!")
#		elif os.path.isfile(myroot):	raise IOError("File "+myroot+" exists!")
		myargs.extend(["-d", dirname, zipfilename])
	else:
#		myargs = UNZIP[:]
#		if junk_paths: myargs.append('-j')
		myargs.append(zipfilename)
	return Popen(myargs, cwd=cwd)
#
import sys
def main(args, assume_owndirs=False, stderr=sys.stderr):
	unzipme = [] # tuples of (cwd, zipfilename, into_own_directory)
	for arg in args:
		for root, dirs, files in os.walk(arg):
			exts = Counter(os.path.splitext(fn)[-1].upper() for fn in files)
			if '.ZIP' in exts:
				local_zipfiles = [fn for fn in files if os.path.splitext(fn)[-1].upper() == '.ZIP']
				if local_zipfiles:
					if assume_owndirs and (len(files) == 1) and not dirs:
						unzipme.extend((root,fn,False) for fn in local_zipfiles)
					else:
						unzipme.extend((root,fn,True) for fn in local_zipfiles)
				else: print >>stderr, "No zip files found in", root
	successes, skipped = [], []
	for cwd, zipfilename, into_own_directory in unzipme:
		zipfilepath = os.path.join(cwd, zipfilename)
		try:
			proc = unzipper(zipfilename, cwd=cwd, into_own_directory=into_own_directory)
			cmdline = proc.cmdline
			myreturn = proc.wait()
			if myreturn:
				print >>stderr, zipfilepath, 'failed:', cmdline or "(no command line)", "returned", myreturn
			else:
				successes.append(zipfilepath)
				delete_file(zipfilepath, no_confirm=True) # , silent=True)
		except IOError as e:
			print >>stderr, "{} skipped: {}".format(zipfilepath, e)
			skipped.append(zipfilepath)
	print
	print "{} files successfully unzipped:".format(len(successes))
	for fn in successes: print fn
	print
	if skipped:
		print "{} files skipped:".format(len(skipped))
		for fn in skipped: print fn
		print
if __name__ == '__main__':
	args = sys.argv[1:] or ['.']
	main(args)

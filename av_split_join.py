#!env python
import os.path
import subprocess

from local.flatten import flatten
from local.xglob import glob

def find_asfbin_executable(paths = []):
	if not paths:
		paths = [ 'asfbin', 'asfbin.exe' ]
		programfiles = os.path.expandvars('%ProgramFiles%')
		search_files = [ 'asfbin*\\asfbin.exe' ]
		paths.extend(glob(os.path.join(programfiles, _) for _ in search_files))
	latest = []
	for f in paths:
		print f
		if os.path.exists(f):
			# Since it exits with error 12, we have to catch an exception:
			try:
				output = subprocess.check_output((f, '-h'))
				asfbin_help = output.splitlines()
			except CalledProcessError as e:
				asfbin_help = e.output.splitlines()
			#
			asfbin_version = asfbin_help[0]
			if latest < [asfbin_version, f]:
				latest = [asfbin_version, f]
	assert latest
	return latest[-1]
#
def find_mkvmerge_executable(paths = []):
	if not paths:
		paths = [ 'mkvmerge', 'mkvmerge.exe' ]
		programfiles = os.path.expandvars('%ProgramFiles%')
		search_files = [ 'MeGUI*\\tools\\mkvmerge\\mkvmerge.exe',
						 'StaxRip*\\Applications\\MKVtoolnix\\mkvmerge.exe' ]
		paths.extend(glob(os.path.join(programfiles, _) for _ in search_files))
	latest = []
	for f in paths:
		if os.path.exists(f):
			try:
				output = subprocess.check_output((f, '--version')).splitlines()
				mkvmerge_version = output[0]
			except CalledProcessError as e:
				continue
			if latest < [mkvmerge_version, f]:
				latest = [mkvmerge_version, f]
	assert latest
	return latest[-1]
#
def find_mp4box_executable(paths = []):
	if not paths:
		paths = [ 'mp4box', 'MP4Box.exe' ]
		programfiles = os.path.expandvars('%ProgramFiles%')
		search_files = [ 'GPAC*\\MP4Box.exe',
						 'MeGUI*\\tools\\mp4box\\MP4Box.exe',
						 'MP4Box*\\MP4Box.exe',
						 'StaxRip*\\Applications\\MP4Box\\MP4Box.exe' ]
		paths.extend(glob(os.path.join(programfiles, _) for _ in search_files))
	latest = []
	for f in paths:
		if os.path.exists(f):
			# Some versions output to stdout, others to stderr
			try:
				output = subprocess.check_output((f, '-version'), stderr=subprocess.STDOUT).splitlines() #
				mp4box_version = output[0]
			except CalledProcessError as e:
				continue
			if latest < [mp4box_version, f]:
				latest = [mp4box_version, f]
	assert latest
	return latest[-1]
#
"""asfbin has a -s option to take a list of segments"""
def asfbin_join_syntax(args, fileout):
	asfbin_args = [('-i', _) for _ in args]
	asfbin_args.append(('-o', fileout))
	return list(flatten(asfbin_args))
def mkvmerge_split_syntax(filein,
						  pairs,
						  fileout='',
						  split_mode='parts',
						  one_file=True):
	section_sep = ',+' if one_file else ','
	if not fileout:
		filepart, ext = os.path.splitext(filein)
		fileout = filepart+'.cut'+ext
	mkvmerge_args = [ '-o', fileout ]
	mkvmerge_args.append('--split')
	if not one_file:
		mkvmerge_args.append('--link')
	mkvmerge_args.append(split_mode+':'+section_sep.join('{}-{}'.format(s,e) for s,e in pairs))
	mkvmerge_args.append(filein)
	return mkvmerge_args
def mp4box_join_syntax(args, fileout):
	mp4box_args = [('-cat', _) for _ in args]
	mp4box_args.append(('-new', '-out', fileout))
	return list(flatten(mp4box_args))
#
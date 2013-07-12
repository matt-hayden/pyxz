#!env python
import os.path

from media_locations import *

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
	#			mkvmerge_version = [ _ for _ in check_output((f, '--version')).splitlines() if _ ]
				mkvmerge_version = check_output((f, '--version')).splitlines()[0]
			except CalledProcessError as e:
				continue
			if latest < [mkvmerge_version, f]:
				latest = [mkvmerge_version, f]
	return latest[-1]
def get_split_syntax(filein,
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
if __name__=='__main__':
	import sys
	
	mkvmerge_executable = find_mkvmerge_executable()
	args = sys.argv[1:]
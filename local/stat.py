from datetime import datetime
import os

def stat(*args):
	stat = os.stat(*args)
	mode = [ int(c) for c in oct(stat.st_mode) ]
	atime = datetime.fromtimestamp(stat.st_atime)
	mtime = datetime.fromtimestamp(stat.st_mtime)
	ctime = datetime.fromtimestamp(stat.st_ctime)
	return os.stat_result((mode, stat.st_ino, stat.st_dev, stat.st_nlink,
						   stat.st_uid, stat.st_gid, stat.st_size, atime, mtime,
						   ctime))
def isdir(*args):
	st = stat(*args)
	return st if st.st_mode[-5] & 4 else False
def isfile(*args):
	st = stat(*args)
	return st if st.st_mode[-5] & 1 else False

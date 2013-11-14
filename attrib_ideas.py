#!env python
from datetime import datetime
import os
import os.path
import cPickle as pickle

from windows_file_ownership import *

import local.Excel, local.zip

#pickle_protocol = -1

def create_new_attrib_file(path, fileout=None):
	assert os.path.exists(path)
	now = datetime.now()
	stat = os.stat(path)
	isdir = stat.st_mode & (4<<12)
	attrib = { 'path':path, 'stat_history':[] }
	attrib['stat_history'].append((now, stat))
	attrib['owner'] = get_owner(path)
	if not isdir:
		dirname, basename = os.path.split(path)
		filepart, ext = os.path.splitext(path)
		if local.zip.zipfile.is_zipfile(path):
			zf = local.zip.zipfile.ZipFile(path)
			filelist = [(zi.filename, zi.file_size, local.zip.parse_zipinfo_date(zi)) for zi in zf.infolist()]
			attrib['content'] = filelist
		if ext.upper() in ('.XLS', '.XLSX'):
			# get names of worksheets
			wb = local.Excel.load_workbook(path)
			current_sheetnames = [ws.title.title() for ws in wb.worksheets]
			if current_sheetnames:
				previous_sheetnames = attrib.get('content', [])
				if current_sheetnames != previous_sheetnames:
					print "Worksheets changed from {} to {}".format(previous_sheetnames, current_sheetnames)
					attrib['content'] = current_sheetnames
	#
	if not fileout:
		if isdir: fileout = os.path.join(path, '.attrib')
		else: fileout = path+'.attrib'
	assert fileout
	with open(fileout, 'wb') as fo:
#		pickle.dump(attrib, fo, protocol=pickle_protocol)
		pickle.dump(attrib, fo)
def load_attrib_file(path):
	if path.endswith('.attrib'):
		attrib_file = path
	else:
		now = datetime.now()
		stat = os.stat(path)
		isdir = stat.st_mode & (4<<12)
		if isdir: attrib_file = os.path.join(path, '.attrib')
		else: attrib_file = path+'.attrib'
	with open(attrib_file) as fi:
		attrib = pickle.load(fi)
	attrib['stat_history'].append((now, stat))
	return attrib
if __name__ == '__main__':
	import sys
	args = sys.argv[1:]
	
	for arg in args:
#		create_new_attrib_file(arg)
		attrib = load_attrib_file(arg)
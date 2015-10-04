#!/usr/bin/env python3
import os, os.path

from jpeg_tools import *

import sys

def pad_jpeg(filename, new_size, max_comment=65000, file_size=None, fillchar=b'\0'):
	if file_size is None:
		file_size = os.path.getsize(filename)
	while file_size < new_size:
		content_chunk_size = new_size - file_size - 4
		assert 0 < content_chunk_size
		if max_comment < content_chunk_size:
			content_chunk_size = max_comment
		content = fillchar*content_chunk_size
		output = subprocess.check_output(['wrjpgcom', filename], input=content)
		#os.rename(filename, filename+'.bkp')
		with open(filename, 'wb') as fo:
			fo.write(output)
		file_size += content_chunk_size+4
	assert os.path.getsize(filename) == new_size
def fudge_jpeg(filename):
	orig_size, new_size = optimize_jpeg(arg)
	if new_size:
		comment_jpeg(filename, 'PADDING STARTS HERE'.encode('UTF-8'))
		pad_jpeg(filename, orig_size)
		for k, v in get_jpeg_comments(filename).items():
			print(k, v[:80])
	else:
		print(filename, "could not be optimized")
#
for arg in sys.argv[1:]:
	fudge_jpeg(arg)

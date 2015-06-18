#!/usr/bin/env python3
import os, os.path
import subprocess

def comment_jpeg(filename, comment, max_comment=65000):
	"""
	comment can be binary, or with .encode('UTF-8'), a string
	"""
	while max_comment < len(comment):
		part, comment = comment[:max_comment], comment[max_comment:]
		comment_jpeg(filename, part, max_comment)
	output = subprocess.check_output(['wrjpgcom', filename], input=comment)
	with open(filename, 'wb') as fo:
		fo.write(output)
def get_jpeg_comments(filename):
	return dict(enumerate(subprocess.check_output(['rdjpgcom', filename]).splitlines()))
def optimize_jpeg(filename, flag='-optimize'):
	orig_size = os.path.getsize(filename)
	output = subprocess.check_output(['jpegtran', '-optimize', filename])
	if len(output) < orig_size:
		os.rename(filename, filename+'.bkp')
		with open(filename, 'wb') as fo:
			fo.write(output)
		return orig_size, len(output)
	else:
		return None, None

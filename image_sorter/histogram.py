#!/usr/bin/env python
import base64
import textwrap

import cv2
import numpy as np

R, G, B = 2, 1, 0
alpha = 3

def get_histograms(filename, mask=None, planes=[R, G, B]):
	if planes:
		img = cv2.imread(filename)
		denom = img.size/3
	else:
		img = cv2.imread(filename, 0)
		denom = img.size
	return { c: cv2.calcHist([img],[c],mask,[256],[0,256])/denom for c in (planes or [0]) }
def get_compressed_histogram(*args, **kwargs):
	def _iter(histos=get_histograms(*args, **kwargs)):
		prev_p, c = alpha, 0
		for i in range(256):
			m, p = max( (a[i], p) for p, a in histos.iteritems() )
			if m == 0:
				p = alpha
			if p == prev_p:
				c += 1
			else:
				if c:
					yield c, prev_p
				c = 1
			prev_p = p
		yield c, p
	return np.array(list(_iter()), dtype=((np.uint8, np.uint8)) )
def print_pairs(pairs, symbols={R:'r', G:'g', B:'b', alpha:'0'} ):
	text = ''
	for c, p in pairs:
		text += symbols[p]*c
	print textwrap.fill(text)
if __name__ == '__main__':
	import sys
	alternate_size = 256/8*4
	for arg in sys.argv[1:]:
		pairs = get_compressed_histogram(arg)
		#print_pairs(pairs)
		try:
			text = base64.b64encode(pairs.tobytes())
		except:
			text = base64.b64encode(pairs.tostring())
		if alternate_size < pairs.nbytes:
			print "Alternate would be smaller than", pairs.nbytes
		else:
			print pairs.nbytes, "bytes"
			print pairs


#!/usr/bin/env python
import textwrap

import cv2
import numpy as np

R, G, B = 2, 1, 0
alpha = 3

def load(filename, mask=None, planes=[R, G, B]):
	if planes:
		image = cv2.imread(filename)
		denom = image.size/3
	else:
		image = cv2.imread(filename, 0)
		denom = image.size
	return image, { c: cv2.calcHist([image], [c], mask, [256], [0,256])/denom for c in (planes or [0]) }

def dominant_plane(*args, **kwargs):
	def _iter(histos):
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
	image, histos = load(*args, **kwargs)
	return image, np.array(list(_iter(histos)), dtype=((np.uint8, np.uint8)) )

def print_pairs(pairs, symbols={R:'r', G:'g', B:'b', alpha:'0'} ):
	text = ''.join(symbols[p]*c for c, p in pairs)
	print textwrap.fill(text)

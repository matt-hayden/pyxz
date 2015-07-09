#!/usr/bin/env python
import base64
import os, os.path

import numpy as np

from edge_density import edge_density_by_axis
from histogram import dominant_plane

class ImgHashBase:
	def __init__(self, filename=None):
		self.edges = [[], []]
		if filename is not None:
			self.from_file(filename)
	def from_file(self, filename):
		_, self.filename = os.path.split(filename)
		image, self.dominant_plane = dominant_plane(filename)
		self.edges, self.median = edge_density_by_axis(image)
	def astuple(self):
		return self.edges+[self.dominant_plane, self.median ]
	@property
	def width(self):
		return 2*len(self.edges[0])
	@property
	def height(self):
		return 2*len(self.edges[1])
#
class ImgHash(ImgHashBase):
	header = 'ImgHash' # string expected at the beginning of a hash
	sep = '?'
	def pack(self, sep='', encoder=base64.b64encode):
		s = [self.header, self.filename]
		t = self.astuple()
		try:
			s.extend(encoder(a.tobytes()) for a in t) # numpy 1.9
		except:
			s.extend(encoder(a.tostring()) for a in t) # numpy 1.7
		return (sep or self.sep).join(s)
	@staticmethod
	def unpack(text, sep='', decoder=base64.b64decode, dtype=np.uint8):
		members = text.split(sep or ImgHash.sep)
		assert members.pop(0) == ImgHash.header
		f = members.pop(0)
		return ImgHash.from_tuple( [ np.frombuffer(decoder(s), dtype=dtype) if s else None for s in members ], filename=f)
	@staticmethod
	def from_tuple(tuple, filename=''):
		# How to create an object without loading:
		r = ImgHash()
		r.filename = filename
		assert len(r.edges) == 2
		#
		r.edges[0], r.edges[1], r.dominant_plane, r.median = tuple
		return r
	def __str__(self):
		#return "ImgHash.unpack('{}')".format(self.pack())
		return "ImgHash('{}')".format(self.filename)
#
if __name__ == '__main__':
	import sys
	for arg in sys.argv[1:]:
		h = ImgHash(arg)
		print h, h.width, h.height
		p = h.pack()
		print p
		u = ImgHash.unpack(p)
		print u, h.width, h.height
		print

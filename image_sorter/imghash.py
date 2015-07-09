#!/usr/bin/env python
import base64

#import cv2
import numpy as np

from edge_density import edge_density_by_axis
from histogram import dominant_plane

class ImgHashBase:
	def __init__(self, filename=None):
		if filename is not None:
			self.from_file(filename)
		return self
	def from_file(self, filename):
		self.filename = filename
		image, self.dominant_plane = dominant_plane(filename)
		self.edges, self.median = edge_density_by_axis(image)
	def astuple(self):
		return [self.edges, self.dominant_plane, self.median]
	@property
	def width(self):
		return len(self.edges[0])
	@property
	def height(self):
		return len(self.edges[1])
	
class ImgHash(ImgHashBase):
	def pack(self, sep='/', encoder=base64.b64encode):
		t = self.astuple()
		try:
			s = [encoder(a.tobytes()) for a in t] # numpy 1.9
		except:
			s = [encoder(a.tostring()) for a in t] # numpy 1.7
		return sep.join(s)
	@staticmethod
	def unpack(text, sep='/', decoder=base64.b64decodestring, dtype=np.uint8):
		return ImgHash.from_tuple([ np.frombuffer(base64.decodestring(s), dtype=dtype) for s in text.split(sep) ])
	@staticmethod
	def from_tuple(tuple):
		r = ImgHash()
		r.edges, r.dominant_plane, r.median = tuple
		return r
	def __str__(self):
		return "ImgHash.unpack('{}')".format(self.pack())
	def __repr__(self):
		return "ImgHash('{}')".format(self.filename)
#
if __name__ == '__main__':
	import sys
	for arg in sys.argv[1:]:
		h = ImgHash(arg)
		print h, h.pack()
		print

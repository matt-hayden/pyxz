#!/usr/bin/env python3
import os, os.path

from PIL import Image, ImageStat
import numpy as np

from tools import *


def get_means(filename):
	with Image.open(grayscale(filename)) as fi:
		W, H = fi.size
		stat = ImageStat.Stat(fi)
		#mean, stdev = stat.mean[0], stat.stdev[0]
		mean = stat.mean[0]
		#sumX, sumY = [0]*W, [0]*H
		sumX, sumY = np.zeros(W), np.zeros(H)
		image = fi.load()
		for x in range(W):
			for y in range(H):
				pv = image[x, y]
				sumX[x] += pv
				sumY[y] += pv
	return mean, [(x/H-mean) for x in sumX], [(y/W-mean) for y in sumY]
class ImgHash:
	def __init__(self, filename=None):
		if filename and os.path.isfile(filename):
			self.from_image(filename)
	def from_image(self, filename):
		self.filename = filename
		self.mean, my_x, my_y = get_means(filename)
		self.x = np.array(my_x, dtype=np.int8)
		self.y = np.array(my_y, dtype=np.int8)
	@property
	def width(self):
		return len(self.x)
	@property
	def height(self):
		return len(self.y)
	@property
	def size(self):
		return len(self.x), len(self.y)
	def to_visual(self, filename):
		image_out = Image.new('L', self.size, self.mean)
		for x in range(self.width):
			for y in range(self.height):
				value = (self.x[x]+self.y[y])/2 + self.mean
				image_out.putpixel((x,y), value)
		image_out.save(filename)
	def save(self, filename, mode='wb'):
		np.savez(filename, x=self.x, y=self.y, mean=self.mean)
	@staticmethod
	def load(filename, mode='rb'):
		n = ImgHash()
		_, basename = os.path.split(filename)
		n.filename, _ = os.path.splitext(basename)
		members = np.load(filename)
		n.x, n.y, n.mean = members['x'], members['y'], members['mean']
		return n
#
if __name__ == '__main__':
	import sys
	for arg in sys.argv[1:]:
		obj = ImgHash(arg)
		obj.save(arg+'.npz')
		obj.to_visual(arg+'.png')

#!/usr/bin/env python3
from array import array
#from math import sqrt
import pickle

from PIL import Image, ImageStat
import numpy as np

from tools import *


def get_means(filename):
	with Image.open(grayscale(filename)) as fi:
		W, H = fi.size
		stat = ImageStat.Stat(fi)
		#mean, stdev = stat.mean[0], stat.stdev[0]
		mean = stat.mean[0]
		sumX, sumY = [0]*W, [0]*H
		image = fi.load()
		for x in range(W):
			for y in range(H):
				pv = image[x, y]
				sumX[x] += pv
				sumY[y] += pv
	return mean, [(x/H-mean) for x in sumX], [(y/W-mean) for y in sumY]
class container:
	def __init__(self, filename, type_code='b'):
		self.filename = filename
		self.mean, my_x, my_y = get_means(filename)
		self.x = array(type_code, [int(_) for _ in my_x])
		self.y = array(type_code, [int(_) for _ in my_y])
		#self.x = np.ndarray(my_x, 'int')
		#self.y = np.ndarray(my_y, 'int')
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
		with open(filename, mode=mode) as fo:
			pickle.dump(self, fo)
	@staticmethod
	def load(filename, mode='rb'):
		with open(filename, mode=mode) as fi:
			return pickle.load(fi)
#
if __name__ == '__main__':
	import sys
	for arg in sys.argv[1:]:
		obj = container(arg)
		obj.save(arg+'.pickle')
		obj.to_visual(arg+'.png')

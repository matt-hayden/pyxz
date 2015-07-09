
import cv2
import numpy as np
import scipy.ndimage

# Wrapper so ndimage has a resize and getpixel functions

class MyImage:
	def __init__(self, *args, **kwargs):
		self.image = np.transpose(cv2.imread(*args, **kwargs)) # not sure why transpose is necessary
	def getpixel(self, (x, y)):
		return self.image[x][y]
	@property
	def size(self):
		try:
			x, y, _ = self.image.shape
		except:
			x, y = self.image.shape
		return x, y
	def apply(self, f, **kwargs):
		r = f(self.image, **kwargs) # TODO
		self.image = r
	def zoom(self, z):
		r = scipy.ndimage.zoom(self.image, z)
		self.image = r
	def resize(self, newsize, fit='width'): # make this match PIL.Image.resize
		oldsize = self.size
		factors = [ float(n)/o for n, o in zip(newsize, oldsize) ]
		if fit == 'preserve':
			f = min(factors)
		elif fit == 'width':
			f = factors[0]
		elif fit == 'height':
			f = factors[1]
		else: # fit none
			f = factors
		self.zoom(f)

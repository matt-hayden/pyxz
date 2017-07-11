#!env python
"""RGB color class.

This is probably implemented better in another library, i.e. PIL
"""
import re
import sys

import webcolors
#
rgb_regex=re.compile('([#]?(?P<rgb>[0-9A-Fa-f]{1,6}))')
#
class RGB:
	channels = 3
	colors = (256**3)
	def __init__(self, num1, num2=None, num3=None, alpha = None):
		if num3 is not None:
			self.from_RGB(num1,num2,num3,alpha)
		else:
			if type(num1)==int:
				self.from_number(num1)
			else:
				self.from_string(num1)
	def from_RGB(self, num1, num2, num3, alpha=0):
		self.R, self.G, self.B, self.transparency = num1, num2, num3, alpha
	def from_number(self, num):
		self.R = num >> 16
		self.G = (num & 0x00ff00) >> 8
		self.B = (num & 0x0000ff)
	def from_string(self, input):
		m = rgb_regex.match(input)
		if m:
			n = int(m.groupdict()['rgb'], 16)
			self.from_number(n)
		else:
			self.from_RGB(*webcolors.name_to_rgb(input))
	def to_hex(self):
		return '#%06x'%int(self)
	def __int__(self):
		return (self.R<<16)+(self.G<<8)+self.B
	def __str__(self):
		colorcode = self.to_hex()
		try:
			return webcolors.hex_to_name(colorcode)
		except ValueError:
			return colorcode
	def __getitem__(self, key):
		if type(key)==slice:
			iterator = iter(xrange(key.start or 0,
								   self.channels if (key.stop == sys.maxint) else key.stop,
								   key.step or 1))
			return [ self[i] for i in iterator ]
		else:
			if key==0:
				return self.R
			elif key==1:
				return self.G
			elif key==2:
				return self.B
			elif key in (3,-1):
				return self.transparency
	def __setitem__(self, key, new_val):
		if type(key)==slice:
			iterator = iter(xrange(key.start or 0,
								   self.channels if (key.stop == sys.maxint) else key.stop,
								   key.step or 1))
			for i in iterator:
				self[i] = new_val[i]
		else:
			if key==0:
				self.R = new_val
			elif key==1:
				self.G = new_val
			elif key==2:
				self.B = new_val
			elif key in (3, -1):
				self.A = new_val
if __name__ == '__main__':
	new_palette = [ 0x000000,	# Black
					0x004080,	# Blue
					0x40a8a8,	# Green
					0x6ca8c8,	# Aqua
					0xb9a060,	# Red
					0x6000d2,	# Purple
					0xaf55a5,	# Yellow
					0xc0c0c0,	# White
					0x808080,	# Gray
					0xff6060,	# Light Red
					0x00ff80,	# Light Green
					0xc0ffff,	# Light Aqua
					0x8080ff,	# Light Blue
					0xff0060,	# Light Purple
					0xffffa8,	# Light Yellow
					0xffffff	# Bright White
					]
	typical_defaults = [ 0x000000, 
						 0x800000, 
						 0x008000, 
						 0x808000, 
						 0x000080, 
						 0x800080, 
						 0x008080, 
						 0xc0c0c0, 
						 0x808080, 
						 0xff0000, 
						 0x00ff00, 
						 0xffff00, 
						 0x0000ff, 
						 0xff00ff, 
						 0x00ffff, 
						 0xffffff ]
	for c in typical_defaults:
		print RGB(c)
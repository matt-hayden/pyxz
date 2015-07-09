#from collections import Counter

import aalib
#import PIL.Image

import cv2

from edge_density import auto_canny

from wrapper import MyImage

import sys
for arg in sys.argv[1:]:
	origin = (0,0)
	#screen = aalib.AsciiScreen(max_width=64, max_height=64)
	screen = aalib.AsciiScreen()
	print "Virtual size:", screen.virtual_size

	image = MyImage(arg, 0) # 0 for grayscale
	print "Image size:", image.size
	image.apply(lambda i : auto_canny(i)[0]) # TODO

	# 0.4 is used only for visual
	#image.resize((screen.virtual_size[0]*0.5, screen.virtual_size[1]), fit='width')
	image.resize(screen.virtual_size, fit=None)
	print "After resize:", image.size

	screen.put_image(origin, image)
	text = screen.render()
	print
	print text

#!/usr/bin/env python3
from . import image_sizes

import sys
for arg, s in image_sizes(sys.argv[1:]):
	print(arg, s)


from PIL import Image

import sys
for arg in sys.argv[1:]:
	i = Image.open(arg)
	s = i.size
	print(arg, s)

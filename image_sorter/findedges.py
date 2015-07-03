import base64

import cv2
import numpy as np

def fold_weights(a, n=None):
	n = n or len(a)
	if n % 2: # odd
		return np.append((a[:n//2]+a[(n//2+1):])/2., a[n//2])
	else: # even
		return (a[:n//2]+a[n//2:])/2.

def imghash(filename):
	img = cv2.imread(filename)
	edges = cv2.Canny(img,100,200)

	mean = img.mean()
	dimweights = [np.mean(edges, axis=a) for a in (0,1)]
	return [fold_weights(a).astype(np.uint8) for a in dimweights], mean
def encode(imghash, sep='/'):
	ws, m = imghash
	try:
		encoded = [base64.b64encode(a.tobytes()) for a in ws]
	except:
		encoded = [base64.b64encode(a.tostring()) for a in ws]
	return sep.join(encoded)
def decode(text, sep='/', dtype=np.uint8):
	return [ np.frombuffer(base64.decodestring(s), dtype=dtype) for s in text.split(sep,1) ], (0,0,0)
#
import sys
for arg in sys.argv[1:]:
	h = imghash(arg)
	t = encode(h)
	d = decode(t)
	print(np.all(d[0][0] == h[0][0]))
	print(np.all(d[0][1] == h[0][1]))

#!/usr/bin/env python
import cv2
import numpy as np

def fold_weights(a, n=None):
	n = n or len(a)
	if n % 2: # odd
		return np.append((a[:n//2]+a[-1:n//2:-1])/2., a[n//2])
	else: # even
		return (a[:n//2]+a[-1:n//2-1:-1])/2.

def auto_canny(image, sigma=0.33):
	'''
	http://www.pyimagesearch.com/2015/04/06/zero-parameter-automatic-canny-edge-detection-with-python-and-opencv/
	'''
	# compute the median of the single channel pixel intensities
	v = np.median(image)

	# apply automatic Canny edge detection using the computed median
	#lower = int(max(0, (1.0 - sigma) * v))
	lower = (1.0 - sigma) * v
	#upper = int(min(255, (1.0 + sigma) * v))
	upper = (1.0 + sigma) * v
	edged = cv2.Canny(image, int(lower) if 0 < lower else 0, int(upper) if upper < 255 else 255)

	# return the edged image
	return edged, v

def edge_density_by_axis(*args, **kwargs):
	edged, v = auto_canny(*args, **kwargs)
	dimweights = [np.mean(edged, axis=a) for a in (0,1)]
	return [fold_weights(a).astype(np.uint8) for a in dimweights], v

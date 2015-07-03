#!/usr/bin/env python3
from itertools import combinations

import fastcluster
from PIL import Image
import numpy as np

from imghash import ImgHash as Instance

def compare(lhs, rhs):
	'''returns a single number, reflexive for each lhs, rhs pair
	'''
	def array_comparator(lhs, rhs):
		return [ (lhs[x] - rhs[x])**2/len(lhs) for x in range(len(lhs)) ]
	assert lhs.width == rhs.width
	assert lhs.height == rhs.height
	results = []
	a = results.append
	diffX = array_comparator(lhs.x, rhs.x)
	diffY = array_comparator(lhs.y, rhs.y)
	a(sum(diffX)+sum(diffY))
	diffX = array_comparator(lhs.x, list(reversed(rhs.x)))
	diffY = array_comparator(lhs.y, rhs.y)
	a(sum(diffX)+sum(diffY))
	return min(results)
def get_distance_matrix(instances, norm=compare):
	n = len(instances)
	m = np.zeros( (n,n) )
	for (a, b) in combinations(range(n), 2):
		r = norm(instances[a], instances[b])
		m[a,b] = m[b,a] = r
	return m
#
def get_cluster(files):
	hashes = [ Instance.load(f) for f in files ]
	results = []
	a = results.append
	print("Cases:")
	for id, c in enumerate(hashes):
		print(id, c.filename)
	print("Clusters:")
	m = get_distance_matrix(hashes)
	print("Linkage matrix is", len(m))
	clustering = fastcluster.linkage(np.sqrt(m), method='complete')
	for pn, (c1, c2, d, n) in enumerate(clustering, start=len(m)):
		print("{:1.0f}+{:1.0f}={:1.0f} with {:1.0f} children at distance {}".format(c1, c2, pn, n, d))
#
if __name__ == '__main__':
	import sys
	get_cluster(sys.argv[1:])

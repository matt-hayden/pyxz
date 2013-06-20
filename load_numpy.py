#!env python
from collections import namedtuple
from logging import debug, info, warning, error, critical
import numpy as np

def load_numpy(*args, **kwargs):
	"""
	Slight wrapper around numpy.load that allows attribute access. Attribute
	names are taken from the numpy dtype.
	"""
	debug("Opening load_numpy")
	debug("args = {}".format(args))
	if kwargs:
		debug("kwargs = {}".format(kwargs))
	table = np.load(*args, **kwargs)
	factory = namedtuple('Row', table.dtype.names)
	for row in table:
		yield factory(*row)
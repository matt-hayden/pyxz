#!env python
import collections
import datetime
import decimal

import numpy as np

from sanitize import sql_field_sanitize

def np_dtype_from_ODBC_desc(desc, sanitize=sql_field_sanitize):
	"""
	See http://docs.scipy.org/doc/numpy/user/basics.types.html
	"""
	name, type_code, display_size, internal_size, precision, scale, null_ok = desc
	if type_code == bool:
		dtype = np.bool
	elif type_code == int:
		if internal_size > 10:
			dtype = np.int64
			warning("Integer precision={} not implemented, using 64 bits".format(internal_size))
		elif 5 < internal_size <= 10:
			dtype = np.int32
		elif 3 < internal_size <= 5:
			dtype = np.int16
		elif internal_size <= 3:
			dtype = np.int8
	elif type_code == float:
		if internal_size > 53:
			dtype = np.float64
			warning("Floating point precision={} not implemented, using 64 bits".format(internal_size))
		elif 23 < internal_size <= 53:
			dtype = np.float64
		elif 10 < internal_size <= 23:
			dtype = np.float32
		elif internal_size <= 10:
			dtype = np.float16
	elif isinstance(type_code, basestring):
		dtype = ('S', internal_size)
	elif type_code == unicode:
		dtype = ('U', internal_size)
	elif type_code == datetime.datetime:
		dtype = 'datetime64[s]' # the subtype is important
	elif type_code == decimal.Decimal:
		dtype = ('S', 255)
	else:
		raise NotImplementedError("Edit np_dtype_from_ODBC_desc to support the class {}".format(desc))
	return sanitize(name, pass_brackets_through=False, pass_string_parts_through=None), dtype
#
def np_fetchone(*args, **kwargs):
	"""
	Slight wrapper around np.load that allows attribute access. Attribute
	names are taken from the np dtype if possible. NPZ file are handled
	transparently. The best way to deal with NPZ is to pass the name= keyword
	argument. Otherwise, look for the default 'arr_0'. Lastly, return the
	largest element.
	"""
	element_name = kwargs.pop('name', 'arr_0')
	loaded = np.load(*args, **kwargs)
	if isinstance(loaded, np.lib.npyio.NpzFile):
		fs = loaded.files
		if fs:
			if element_name not in fs:
				_, element_name = max((loaded[f].size, f) for f in fs)
			table = loaded[element_name] 
	else:
		table = loaded
	return np_attributize(table)
#
def np_attributize(arraylike):
	names = arraylike.dtype.names
	if names:
		factory = collections.namedtuple('Row', names, rename=True)
		return (factory(*row) for row in arraylike)
	else:
		return arraylike
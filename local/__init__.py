#!env python
"""
This is a toy module containing useful but not necessarily inter-related
extensions to the Python standard library.
Some modules are prefixed with x to avoid collisions with the standard library.

For specific file and data formats:
	Excel
	MP3
	xcsv

For general formats:
	md5sum
	MediaInfo
	odbc
	xzip

Arithmetic and human-friendliness:
	rgb
	units

Text transformations:
	explode_table
	sanitize

Filesystem operations:
	Hierarchy
	VolumeMaker
	walk
	xstat

Command-line operations:
	console
	xglob

Extensions to the standard library:
	xConfigParser
	xcollections
	xdatetime
	xmimetypes
	xsched

Numpy support:
	xnp

Generalizations (not necessarily preferred in production):
	Interval
	cacher
	config
	coroutines
	flatten

"""
from logging import debug, info, warning, error, critical
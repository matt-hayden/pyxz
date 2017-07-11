#!env python
from os import walk
from os.path import isdir, join
import sys

try:
	from win32file import GetFileAttributes, SetFileAttributes
	from win32con import FILE_ATTRIBUTE_ARCHIVE, FILE_ATTRIBUTE_READONLY
except ImportError:
	print >>sys.stderr, "Unsupported on %s" % (sys.executable)
	import pdb; pdb.set_trace()
#
recurse = True
#
def ArchiveBit(filename):
	return GetFileAttributes(filename) & FILE_ATTRIBUTE_ARCHIVE
def ReadOnlyBit(filename):
	return GetFileAttributes(filename) & FILE_ATTRIBUTE_READONLY
#
def SetAttributes(filename, new_attributes, old_attributes = None):
	if old_attributes is None:
		old_attributes = GetFileAttributes(filename)
	if new_attributes:
		SetFileAttributes(filename, old_attributes | new_attributes)
#
def ClearAttributes(filename, new_attributes, old_attributes = None):
	if old_attributes is None:
		old_attributes = GetFileAttributes(filename)
	if new_attributes:
		SetFileAttributes(filename, old_attributes & ~new_attributes)
#
def ToggleAttributeBits(filename, new_attributes, old_attributes = None):
	if old_attributes is None:
		old_attributes = GetFileAttributes(filename)
	if new_attributes:
		SetFileAttributes(filename, old_attributes^new_attributes)
#
if __name__ == '__main__':
	for arg in sys.argv[1:]:
		if isdir(arg) and recurse:
			for r, dl, fl in walk(arg):
				for f in fl:
					#ToggleAttributeBits(join(r,f), FILE_ATTRIBUTE_ARCHIVE)
					ClearAttributes(join(r,f), FILE_ATTRIBUTE_ARCHIVE)
		else:
			#ToggleAttributeBits(arg, FILE_ATTRIBUTE_ARCHIVE)
			ClearAttributes(arg, FILE_ATTRIBUTE_ARCHIVE)
#
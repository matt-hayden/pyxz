#!env python
from os import walk
from os.path import isdir, join
import sys
from win32file import GetFileAttributes, SetFileAttributes
from win32con import FILE_ATTRIBUTE_ARCHIVE, FILE_ATTRIBUTE_READONLY

def ArchiveBit(filename):
	return GetFileAttributes(filename) & FILE_ATTRIBUTE_ARCHIVE
def ReadOnlyBit(filename):
	return GetFileAttributes(filename) & FILE_ATTRIBUTE_READONLY
def ToggleAttributeBits(filename, new_attributes, old_attributes = None):
	if old_attributes is None:
		old_attributes = GetFileAttributes(filename)
	if new_attributes:
		SetFileAttributes(filename, old_attributes^new_attributes)
if __name__ == '__main__':
	for arg in sys.argv[1:]:
		if isdir(arg):
			for r, dl, fl in walk(arg):
				for f in fl:
					ToggleAttributeBits(join(r,f), FILE_ATTRIBUTE_ARCHIVE)
		else:
			ToggleAttributeBits(arg, FILE_ATTRIBUTE_ARCHIVE)
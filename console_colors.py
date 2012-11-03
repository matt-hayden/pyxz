import argparse, sys
from itertools import count, izip
try:
	from _winreg import *
except ImportError:
	print >>sys.stderr, "Windows-only _winreg module required"
#
class WindowsConsoleColor:
	permissions = KEY_ALL_ACCESS
	#permissions = KEY_READ
	value_type = REG_DWORD
	typical_defaults = [ 0x000000, 0x800000, 0x008000, 0x808000, 0x000080, 0x800080, 0x008080, 0xc0c0c0, 0x808080, 0xff0000, 0x00ff00, 0xffff00, 0x0000ff, 0xff00ff, 0x00ffff, 0xffffff ]
	#
	def __init__(self):
		self.key = OpenKey(HKEY_CURRENT_USER, "Console", 0, self.permissions)
	#def __del__(self):
	#	if self.key:
	#		CloseKey(self.key)
	def __getitem__(self, index):
		val, val_type = QueryValueEx(self.key, "ColorTable%02d" % index)
		return val
	def __setitem__(self, index, new_value):
		SetValueEx(self.key, "ColorTable%02d" % index, 0, self.value_type, new_value)
	### These should be replaced with slice comprehension in getitem and setitem:
	def get_palette(self):
		return [ self[x] for x in range(16) ]
	def set_palette(self, new_palette):
		self.old_values = self.get_palette()
		for n, v in izip(count(0), new_palette):
			self[n] = v
if __name__ == '__main__':
	wcc = WindowsConsoleColor()
	my_palette = [ 0x000000, 0x9e1828, 0xaece92, 0x968a38, 0x414171, 0x963c59, 0x418179, 0xbebebe, 0x666666, 0xcf6171, 0xc5f779, 0xfff796, 0x4186be, 0xcf9ebe, 0x71bebe, 0xffffff ]
	my_palette = wcc.typical_colors
	print "Current palette:", [ "0x%06x" % x for x in wcc.get_palette() ]
	print "Setting palette to: ", [ "0x%06x" % x for x in my_palette ]
	wcc.set_palette(my_palette)
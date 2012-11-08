import re
import sys

try:
	from _winreg import *
except ImportError:
	print >>sys.stderr, "Windows-only _winreg module required"
#
rgb_regex=re.compile('([#]?(?P<rgb>[0-9A-Fa-f]{1,6}))')
#
class WindowsConsoleColor:
	colors = 16
	color_space = (256**3-1)
	permissions = KEY_ALL_ACCESS
	#permissions = KEY_READ
	value_type = REG_DWORD
	typical_defaults = [ 0x000000,	# black
						 0x800000,	# maroon
						 0x008000,	# green
						 0x808000,	# olive
						 0x000080,	# navy
						 0x800080,	# purple
						 0x008080,	# teal
						 0xc0c0c0,	# silver
						 0x808080,	# grey
						 0xff0000,	# red
						 0x00ff00,	# lime
						 0xffff00,	# yellow
						 0x0000ff,	# blue
						 0xff00ff,	# magenta
						 0x00ffff,	# aqua
						 0xffffff	# white
						 ]
	#
	@staticmethod
	def GetSettingsByApplication():
		regkey = OpenKey(HKEY_CURRENT_USER, "Console", 0, KEY_READ)
		index = 0
		for i in range(1024):
			try:
				yield EnumKey(regkey,index)
				index += 1
			except WindowsError:
				raise StopIteration
	#
	def __init__(self, KeyName="Console", Computer=None):
		self.regkey = OpenKey(HKEY_CURRENT_USER, KeyName, 0, self.permissions)
		if Computer:
			self.regkey = ConnectRegistry(Computer, self.regkey)
	#def __del__(self):
	#	if self.regkey:
	#		CloseKey(self.regkey)
	def __getitem__(self, key):
		if type(key)==slice:
			iterator = iter(xrange(key.start or 0,
								   self.colors if (key.stop == sys.maxint) else key.stop,
								   key.step or 1))
			return [ self[i] for i in iterator ]
		else:
			val, val_type = QueryValueEx(self.regkey, "ColorTable%02d" % key)
			return val
	def __setitem__(self, key, new_val):
		if type(key)==slice:
			iterator = iter(xrange(key.start or 0,
								   self.colors if (key.stop == sys.maxint) else key.stop,
								   key.step or 1))
			for i in iterator:
				self[i] = new_val[i]
		else:
			if type(new_val)==string:
				m = rgb_regex.match(new_val)
				if m:
					l = int(m.groupdict()['rgb'])
					if (0 <= l <= self.color_space):
						self[key] = l
				else:
					pass
			else:
				SetValueEx(self.regkey,				# name of key
						   "ColorTable%02d" % key,	# name of subkey
						   0,						# reserved
						   self.value_type,			# colors are integers, see REG_DWORD above
						   new_val
						   )
if __name__ == '__main__':
	wcc = WindowsConsoleColor()
	apps = list(wcc.GetSettingsByApplication())
	print "%d application(s) have custom settings: %r" %(len(apps), apps)
	print "Current palette:", [ "0x%06x" % x for x in wcc[:] ]
	if False:
		new_palette = [ 0x000000,	# Black
						0x004080,	# Blue
						0x40a8a8,	# Green
						0x6ca8c8,	# Aqua
						0xb9a060,	# Red
						0x6000d2,	# Purple
						0xaf55a5,	# Yellow
						0xc0c0c0,	# White
						0x808080,	# Gray
						0xff6060,	# Light Red
						0x00ff80,	# Light Green
						0xc0ffff,	# Light Aqua
						0x8080ff,	# Light Blue
						0xff0060,	# Light Purple
						0xffffa8,	# Light Yellow
						0xffffff	# Bright White
						]
		print "Setting palette to: ", [ "0x%06x" % x for x in new_palette ]
		wcc[:] = new_palette
		print "Now palette is:", [ "0x%06x" % x for x in wcc[:] ]
	if True:
		m = rgb_regex.match('#123456')
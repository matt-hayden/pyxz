import sys

try:
	from _winreg import *
except ImportError:
	print >>sys.stderr, "Windows-only _winreg module required"
#
class WindowsConsoleColor:
	colors = 16
	permissions = KEY_ALL_ACCESS
	#permissions = KEY_READ
	value_type = REG_DWORD
	typical_defaults = [ 0x000000, 
						 0x800000, 
						 0x008000, 
						 0x808000, 
						 0x000080, 
						 0x800080, 
						 0x008080, 
						 0xc0c0c0, 
						 0x808080, 
						 0xff0000, 
						 0x00ff00, 
						 0xffff00, 
						 0x0000ff, 
						 0xff00ff, 
						 0x00ffff, 
						 0xffffff ]
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
	if True:
		new_palette = [ 0x000000,
						0x004080,
						0x40a8a8,
						0x6ca8c8,
						0xb9a060,
						0x6000d2,
						0xaf55a5,
						0xc0c0c0,
						0x808080,
						0x8080ff,
						0x00ff80,
						0xc0ffff,
						0xff6060,
						0xff0060,
						0xffffa8,
						0xffffff ]
		print "Setting palette to: ", [ "0x%06x" % x for x in new_palette ]
		wcc[:] = new_palette
		print "Now palette is:", [ "0x%06x" % x for x in wcc[:] ]
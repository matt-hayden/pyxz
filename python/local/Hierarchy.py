from contextlib import contextmanager
import os.path
from zipfile import ZipFile, ZIP_STORED, ZIP_DEFLATED

"""
Take a directory or a zip-like file and enumerate internal members.
"""

class HierarchyError(Exception):
	pass
class FileLikeHierarchy:
	"""
	Abstract class to be subclassed for more features
	"""
	def __contains__(self, filename):
		return (filename in self.get_filenames())
	def __str__(self):
		return self.filename
	#def close(self):
	#	pass
class FolderHierarchy(FileLikeHierarchy):
	overwrite = False
	def __init__(self, data, **kwargs):
		self.from_folder(dirpath=data, **kwargs)
	def __str__(self):
		return self.dirpath
	#
	def from_folder(self, dirpath, **kwargs):
		self.mode = kwargs.pop('mode', 'rb')
		self.dirpath = dirpath
		if 'w' in self.mode or 'a' in self.mode and not os.path.exists(self.dirpath):
			os.mkdir(self.dirpath)
	def get_filenames(self):
		for r, ds, fs in os.walk(self.dirpath):
			for f in fs:
				yield f
	def open(self, filename):
		return open(os.path.join(self.dirpath, filename), mode=self.mode)
	def write_member(self, path, content):
		"""
		Currently does not handle subdirectories.
		"""
		target = os.path.join(self.dirpath, path)
		if os.path.exists(target) and not self.overwrite:
			raise HierarchyError("%s exists, refusing to overwrite" % path)
		with open(target, mode='wb') as fo:
			fo.write(content)
			
class ZipFileHierarchy(FileLikeHierarchy):
	compression = ZIP_DEFLATED
	overwrite = False
	def __init__(self, data, **kwargs):
		self.from_zipfile(filename=data, **kwargs)
	def close(self):
		self.zipfile.close() # required, or expect corruption
	#
	def from_zipfile(self, filename, **kwargs):
		mode = kwargs.pop('mode', 'r')
		self.filename = filename
		if os.path.exists(self.filename):
			# assume existing file
			if 'w' in mode:
				raise HierarchyError("%s exists, refusing to overwrite" % filename)
			self.zipfile = ZipFile(filename, mode=mode, **kwargs)
		elif 'w' in mode or 'a' in mode:
			# create new file
			self.zipfile = ZipFile(filename, mode=mode, compression=self.compression, **kwargs)
		else:
			raise HierarchyError("%s does not exist" % filename)
		self.comment = self.zipfile.comment
	def get_filenames(self):
		"""
		http://mail.python.org/pipermail/python-dev/2001-March/013776.html
		"""
		_A_SUBDIR = 0x10
		def isdir(zi):
			return (((zi.external_attr & 0xff) & _A_SUBDIR) !=0)
		return (zi.filename for zi in self.zipfile.infolist() if not isdir(zi))
	def open(self, filename, **kwargs):
		"""
		Can also take a ZipInfo object.
		"""
		return self.zipfile.open(filename, **kwargs)
	def write_member(self, path, content):
		if path in self and not self.overwrite:
			raise HierarchyError("%s exists, refusing to overwrite" % path)
		self.zipfile.writestr(path, content)
@contextmanager
def Hierarchy(somepath, **kwargs):
	"""
	Convience function
	"""
	dirname, filename = os.path.split(somepath)
	filepart, extension = os.path.splitext(filename)
	uext = extension.upper()
	if uext == '.ZIP':
		yield ZipFileHierarchy(somepath, **kwargs)
	elif os.path.isdir(somepath):
		yield FolderHierarchy(somepath, **kwargs)
	elif somepath.endswith(os.path.sep) or somepath.endswith('/'):
		yield FolderHierarchy(somepath, **kwargs)
	elif uext == '.D':
		yield FolderHierarchy(somepath, **kwargs)
	else:
		raise HierarchyError("%s not an expected file type!" % somepath)

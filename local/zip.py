import io
from zipfile import ZipFile

def zip_fetchone(filepath, default_extensions = [], **kwargs):
	"""
	Simple helper function to allow ZIP files as file containers. The ZIP file
	must contain a nonambiguous internal member. For example, foo.ZIP must
	include foo, or foo.txt if '.txt' in argument default_extensions.
	The extensions in default_extensions are checked in order.
	"""
	with ZipFile(filepath, 'r') as zi:
		filelist = zi.infolist()
		if len(filelist) == 0:
			raise IOError("File '{}' empty".format(filepath))
		elif 'zip_entry' in kwargs: # can be a filename or ZipInfo object
			bi = zi.open(kwargs.pop('zip_entry'))
		elif len(filelist) == 1:
			bi = zi.open(filelist[0])
		else:
			dirname, filename = os.path.split(filepath)
			basename, ext = os.path.splitext(filename)
			if default_extensions:
				default_filenames = [ basename+ext for ext in default_extensions ]+[basename]
			else:
				default_filenames = [basename]
			# case-insensitive:
			default_filenames = [ f.upper() for f in default_filenames ]
			possible_valid_entries = [ i for i in filelist if i.filename.upper() in default_filenames ]
			if not possible_valid_entries:
				bi = zi.open(filelist[0])
				info("Tried to find a nonambiguous file in {}, resorted to {}".format(filepath, filelist[0]))
			elif len(possible_valid_entries) == 1:
				bi = zi.open(possible_valid_entries[0])
			else:
				listing = ", ".join(possible_valid_entries)
				if len(listing) > 255:
					listing[:252]+"..."
				info("%d candidate members in %s: %s" %(len(possible_valid_entries), filename, listing))
				bi = zi.open(filelist[0])
		return io.TextIOWrapper(bi, newline=None)
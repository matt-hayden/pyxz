#! env python
import csv
import sys
import xml.etree.cElementTree

from windows_clipboard import *

try:
	interactive = sys.flags.interactive or (sys.ps1 is not None)
except AttributeError:
	interactive = False

try:
	from PIL import Image, ImageGrab
	import numpy as np
except ImportError:
	ImageGrab = None	

file_extension = {
	"WAVE": ".wav",
	"ENHMETAFILE": ".wmf",
	"PNG": ".png",
	"JFIF": ".jpeg"
}
preferred_format = ''
#preferred_format = 'HTML format'
with clipboard_manager():
	formats = get_clipboard_formats()
	print >> sys.stderr, formats
	if preferred_format in formats:
		data = clipboard.GetClipboardData(formats[preferred_format])
	else:
		print >> sys.stderr, "{} format not available".format(preferred_format)
		if 'WAVE' in formats:
			data = clipboard.GetClipboardData(clipboard.CF_WAVE)
### Text formats:
		elif 'Csv' in formats:
			data = clipboard.GetClipboardData(formats['Csv'])
			reader = csv.reader(data.splitlines(), dialect='excel-tab')
		elif 'UNICODETEXT' in formats:
			data = clipboard.GetClipboardData(formats['UNICODETEXT'])
		elif 'TEXT' in formats:
			data = clipboard.GetClipboardData(formats['TEXT'])
### Image formats:
		elif set('PNG JFIF DIBV5 DIB BITMAP'.split()).intersection(formats):
			data = None
			image = ImageGrab.grabclipboard()
			size = np.array(image.size)
			if interactive:
				print "The image from the clipboard is in the variable image, with its size in size"
				print "Some example commands include:"
				print "image.resize(2.5*size)"
				print "image.thumbnail((64,64), Image.ANTIALIAS)"
				print "image.save('Banjo.jpg')"
### Meta formats:
		elif 'XML Spreadsheet' in formats:
			data = clipboard.GetClipboardData(formats['XML Spreadsheet'])
			parser = xml.etree.cElementTree.fromstring(data[:-1] if data.endswith('\x00') else data)
		elif 'ENHMETAFILE' in formats:
			data = clipboard.GetClipboardData(clipboard.CF_ENHMETAFILE)
		elif 'CF_HDROP' in formats:
			data = '\n'.join(clipboard.GetClipboardData(clipboard.CF_ENHMETAFILECF_HDROP))
### Default
		else:
			print >> sys.stderr, "No recognized formats in {}".format(formats.keys())
			data = clipboard.GetClipboardData()
if not interactive:
	sys.stdout.write(data)
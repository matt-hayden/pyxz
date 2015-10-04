#! /usr/bin/env python2

"""
Very simple Windows clipboard. The Windows clip command can only copy. This
script can copy and paste. 
"""
from contextlib import contextmanager
import win32clipboard as clipboard

clipboard_format_by_name = {
	"BITMAP":           clipboard.CF_BITMAP,
	"DIB":              clipboard.CF_DIB,
	"DIBV5":            clipboard.CF_DIBV5,
	"DIF":              clipboard.CF_DIF,
	"DSPBITMAP":        clipboard.CF_DSPBITMAP,
	"DSPENHMETAFILE":   clipboard.CF_DSPENHMETAFILE,
	"DSPMETAFILEPICT":  clipboard.CF_DSPMETAFILEPICT,
	"DSPTEXT":          clipboard.CF_DSPTEXT,
	"ENHMETAFILE":      clipboard.CF_ENHMETAFILE,
	"HDROP":            clipboard.CF_HDROP,
	"LOCALE":           clipboard.CF_LOCALE,
	"METAFILEPICT":     clipboard.CF_METAFILEPICT,
	"OEMTEXT":          clipboard.CF_OEMTEXT,
	"OWNERDISPLAY":     clipboard.CF_OWNERDISPLAY,
	"PALETTE":          clipboard.CF_PALETTE,
	"PENDATA":          clipboard.CF_PENDATA,
	"RIFF":             clipboard.CF_RIFF,
	"SYLK":             clipboard.CF_SYLK,
	"TEXT":             clipboard.CF_TEXT,
	"TIFF":             clipboard.CF_TIFF,
	"UNICODETEXT":      clipboard.CF_UNICODETEXT,
	"WAVE":             clipboard.CF_WAVE
}


@contextmanager
def clipboard_manager():
	yield clipboard.OpenClipboard()
	clipboard.CloseClipboard()

#
if __name__ == '__main__':
    import sys
    args, exit = sys.argv[1:], sys.exit
    stdin, stdout, stderr = sys.stdin, sys.stdout, sys.stderr
    if not stdin.isatty(): # if stdin is redirected
        with clipboard_manager():
            clipboard.EmptyClipboard()
        with clipboard_manager():
            #handle = clipboard.SetClipboardData(clipboard_format_by_name['TEXT'], stdin.read())
            handle = clipboard.SetClipboardText(stdin.read())
            if False:
                print handle
    else:
        with clipboard_manager():
            assert clipboard.IsClipboardFormatAvailable(clipboard_format_by_name['TEXT'])
            for line in clipboard.GetClipboardData().splitlines():
                print line

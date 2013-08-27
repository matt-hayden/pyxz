#! env python
"""
Wrapper to get the size of the current terminal window.

Availability:
	UNIX: curses and console tools
	Win32: win32console if PyWin32 installed or a fallback
"""
from collections import deque
import os
import struct
import sys
#
def get_win32console_size():
	"""
	http://nullege.com/codes/search/win32console.GetStdHandle
	"""
	try:
		import win32console
		# Query stderr to avoid problems with redirections
		screenbuf = win32console.GetStdHandle(win32console.STD_ERROR_HANDLE)
		window = screenbuf.GetConsoleScreenBufferInfo()['Window']
		columns = window.Right - window.Left + 1
		rows = window.Bottom - window.Top + 1
		return (rows, columns)
	except ImportError:
		from ctypes import windll, create_string_buffer
		# stdin handle is -10
		# stdout handle is -11
		# stderr handle is -12
		h = windll.kernel32.GetStdHandle(-12)
		csbi = create_string_buffer(22)
		res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
		if res:
			(bufx, bufy, curx, cury, wattr,
			left, top, right, bottom,
			maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
			sizex = right - left + 1
			sizey = bottom - top + 1
			return (sizey, sizex)
#
def get_termios_size():
	"""
	http://pdos.csail.mit.edu/~cblake/cls/cls.py
	"""
	def ioctl_GWINSZ(fd):					#### TABULATION FUNCTIONS
		try:								### Discover terminal width
			import fcntl, termios, struct	#, os
			cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
		except:
			return None
		return cr
	cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)  # try open fds
	if not cr:                                                  # ...then ctty
		try:
			fd = os.open(os.ctermid(), os.O_RDONLY)
			cr = ioctl_GWINSZ(fd)
			os.close(fd)
		except:
			return None
	return cr[1], cr[0]
#
def get_terminal_size(default = None):
	rc = get_termios_size()
	if not rc:
		try:
			rc = os.popen('stty size', 'r').read().split()
		except:
			pass
	if not rc:
		rc = get_win32console_size()
	if not rc:
		try:
			rc = os.environ['LINES'], os.environ['COLUMNS']
		except:
			pass
	return rc or default
#
def to_columns(iterable,
			   num_columns=None,
			   sep=' ',
			   pad='',
			   num_chars=None):
	"""
	Formats elements of an iterable into a table, like the short output of 'ls'
	"""
	# Rinse:
	if isinstance(iterable, basestring): iterable = iterable.splitlines()
	else: iterable = list(iterable)
	[ s.replace('\t',' '*8) for s in iterable ]
	col_width = max(len(str(i)) for i in iterable)+len(sep)
	length = len(iterable)
	
	# Lather:
	if not num_columns:
		if not num_chars:
			term_rows, num_chars = get_terminal_size()
			if pad: num_chars -= 2*len(pad)
		num_columns = num_chars//col_width
	if num_columns < 1: num_columns = 1
	### TODO:
	rows = (length//num_columns)+1
	rows = int(round(length/num_columns))
	###
	partitioned = [iterable[c:c+rows] for c in xrange(0,length,rows)]
	width_by_partition = [ (max(len(x) for x in ri), ri) for ri in partitioned ]
	partitioned = [ [x.ljust(i) for x in col_width] for i, col_width in width_by_partition ]
	if len(partitioned) > 1:
		empty_values_on_last_row = rows - len(partitioned[-1])
		partitioned[-1].extend(['']*empty_values_on_last_row)
	lines = (sep.join(x) for x in zip(*partitioned))
	if pad: return os.linesep.join(pad+line+pad for line in lines)
	else:   return os.linesep.join(lines)
def tail(iterable, rows=get_terminal_size()[0]):
	return deque(iterable, rows)
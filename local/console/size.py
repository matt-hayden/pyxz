#! env python
"""
Wrapper to get the size of the current terminal window.

Availability:
	UNIX: curses and console tools
	Win32: win32console if PyWin32 installed or a fallback
"""
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
			   sep=None, 
			   term_columns=None):
	"""
	Formats elements of an iterable into a table, like the short output of 'ls'
	"""
	sl = max(len(str(_)) for _ in iterable)
	l = len(iterable)
	if not num_columns:
		if not term_columns:
			term_rows, term_columns = get_terminal_size()
		num_columns = term_columns//sl
	if num_columns < 1: num_columns = 1
	rows = (l//num_columns)+1
	partitioned = [iterable[_:_+rows] for _ in xrange(0,l,rows)]
	if sep is None:
		width_by_partition = [ (max(len(x) for x in _), _) for _ in partitioned ]
		partitioned = [ [x.ljust(j) for x in _] for j, _ in width_by_partition ]
		sep = ' '
	lines = (sep.join(x) for x in zip(*partitioned))
	return '\n'.join(lines)
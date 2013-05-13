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
def condense_string(text, width):
	ss = text.split()
	if not ss:
		return text
	mwl = max(len(_) for _ in ss)
	for wl in range(mwl, 2, -1):
		ns = [ _[:wl] for _ in ss ]
		nt = ' '.join(ns)
		if len(nt) < width:
			return nt
	return nt[:width]
#
class redirect_terminal():
	"""
	http://stackoverflow.com/questions/6796492/python-temporarily-redirect-stdout-stderr
	with redirect_terminal(stdout=open(os.devnull, 'w')):
		print("You'll never see me")
	"""
	def __init__(self, stdout=None, stderr=None):
		if isinstance(stdout, str):
			stdout_file = stdout
			stdout = open(stdout_file, 'w')
		if isinstance(stderr, str):
			stderr_file = stderr
			stderr = open(stderr_file, 'w')
		self._stdout = stdout or sys.stdout
		self._stderr = stderr or sys.stderr

	def __enter__(self):
		self.old_stdout, self.old_stderr = sys.stdout, sys.stderr
		self.old_stdout.flush(); self.old_stderr.flush()
		sys.stdout, sys.stderr = self._stdout, self._stderr

	def __exit__(self, exc_type, exc_value, traceback):
		self._stdout.flush(); self._stderr.flush()
		sys.stdout = self.old_stdout
		sys.stderr = self.old_stderr
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
def to_columns(iterable, num_columns = None, sep=None, term_columns = None):
	"""
	Formats elements of an iterable into a table, like the short output of 'ls'
	"""
	sl = max(len(str(x)) for x in iterable)
	if not num_columns:
		if not term_columns:
			term_rows, term_columns = get_terminal_size()
		num_columns = term_columns//sl
	if num_columns < 1:
		num_columns = 1
	rows = (len(iterable)//num_columns)+1
	partitioned = [iterable[i:i+rows] for i in xrange(1,len(iterable),rows)]
	if sep is None:
		width_by_partition = [ (max(len(x) for x in el), el) for el in partitioned ]
		partitioned = [ [x.ljust(j) for x in el] for j, el in width_by_partition ]
		sep = ' '
	lines = (sep.join(x) for x in zip(*partitioned))
	return '\n'.join(lines)
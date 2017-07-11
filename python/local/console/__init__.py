import os
import sys

def condense_string(text, width):
	"""
	Smush a long string to fit a maximum width
	"""
	if len(text) <= width: return text
	ss = text.split()
	if not ss: return text[:width]
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
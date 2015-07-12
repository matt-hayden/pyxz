#!/usr/bin/env python
from array import array
import subprocess

fpcalc_executable = 'fpcalc'

class ChromaprintError(Exception):
	pass

class Fingerprint:
	def __init__(self, init):
		self.from_lines(init)
	def from_lines(self, lines, raw=True):
		for line in lines:
			k, v = line.rstrip().split('=', 1)
			assert k and v
			if 'FILE' == k:
				self.filename = v
			elif 'DURATION' == k:
				self.duration = int(v)
			elif 'FINGERPRINT' == k:
				self._set_fingerprint(v)
			else:
				raise ChromaprintError(k+" unexpected")
	def _set_fingerprint(self, v):
		self.fingerprint = v
	def __repr__(self):
		return "<CompressedFingerprint({}, {}, <{}>)>".format(self.filename, self.duration, len(self.fingerprint))
class BinaryFingerprint(Fingerprint):
	typecode = 'i'
	def _set_fingerprint(self, v):
		self.fingerprint = array(self.typecode, (int(m) for m in v.split(',')))
	def __repr__(self):
		return "<Fingerprint({}, {}, <{}>)>".format(self.filename, self.duration, len(self.fingerprint))
#
def output_formatter(lines, r):
	mylines = []
	for line in lines:
		if line.strip():
			mylines.append(line.rstrip())
		else:
			yield r(mylines)
			mylines = []
	if mylines:
		yield r(mylines)

def fpcalcs(filenames, length=None, binary=True):
	commands = [fpcalc_executable]
	if length not in (120, None): # default
		commands += ['-length', length]
	if binary:
		commands += ['-raw']
	proc = subprocess.Popen(commands+filenames, stdout=subprocess.PIPE)
	out, _ = proc.communicate()
	if proc.returncode:
		raise ChromaprintError("Exited {}".format(proc.returncode))
	return sorted(output_formatter(out.splitlines(), BinaryFingerprint if binary else Fingerprint))
if __name__ == '__main__':
	import sys
	for fp in fpcalcs(sys.argv[1:]):
		print fp
		


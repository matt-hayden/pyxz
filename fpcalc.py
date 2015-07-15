#!/usr/bin/env python
from array import array
from multiprocessing import Pool
import os, os.path
import subprocess
import sys

if sys.platform.startswith('win'):
	fpcalc_executable = 'FPCALC.EXE'
else:
	fpcalc_executable = 'fpcalc'

ext = '.fp'

class ChromaprintError(Exception):
	pass

class FingerprintBase:
	def __lt__(self, other):
		return self.fingerprint < other.fingerprint

class Fingerprint(FingerprintBase):
	def __init__(self, init):
		if init:
			if isinstance(init, str):
				if '\n' in init:
					self.from_lines(init.splitlines())
				elif os.path.exists(init):
					self.from_file(init)
			else:
				self.from_lines(init)
	def from_lines(self, lines, encoding='ASCII'):
		for b in lines:
			try:
				line = b.decode(encoding).rstrip()
			except:
				line = b.rstrip()
			k, v = line.split('=', 1)
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
		return "<CompressedFingerprint('{}'), duration {}, size {}>".format(self.filename, self.duration, len(self.fingerprint))
	def to_lines(self):
		return [ '{}={}\n'.format(k, v) for k, v in (('FILE', self.filename), ('DURATION', self.duration), ('FINGERPRINT', self.fingerprint)) ]
	def to_file(self, filename):
		assert not os.path.isfile(filename)
		with open(filename, 'w') as fo:
			fo.writelines(self.to_lines())
	def from_file(self, init):
		if isinstance(init, str):
			fd = open(init)
		else:
			fd = init
		self.from_lines(fd.read().splitlines())

class BinaryFingerprint(Fingerprint):
	typecode = 'i'
	def _set_fingerprint(self, v):
		self.fingerprint = array(self.typecode, (int(m) for m in v.split(',')))
	def __repr__(self):
		return "<Fingerprint('{}'), duration {}, size {}>".format(self.filename, self.duration, len(self.fingerprint))
#
def output_formatter(lines, factory=Fingerprint, results=[]):
	for line in lines:
		if line.strip():
			results.append(line.rstrip())
		else: # split on blank lines
			yield factory(results)
			results = []
	if results: # else last line is blank
		yield factory(results)

def fpcalcs(filenames, length=None, binary=False):
	if isinstance(length, str):
		length = int(length)
	commands = [fpcalc_executable]
	if length:
		commands += [ '-length', str(length) ]
	if binary:
		commands += ['-raw']
	proc = subprocess.Popen(commands+filenames, stdout=subprocess.PIPE)
	out, _ = proc.communicate()
	if proc.returncode:
		raise ChromaprintError("'{}' exited {}".format(' '.join(commands, filenames), proc.returncode))
	return sorted(output_formatter(out.splitlines(), BinaryFingerprint if binary else Fingerprint))
def load(filename, **kwargs):
	fp_file = filename+ext
	if os.path.isfile(fp_file):
		try:
			with open(fp_file) as fi:
				return Fingerprint(fi.read(), **kwargs)
		except: pass
	(fp,) = fpcalcs([filename])
	fp.to_file(fp_file)
	return fp
#
if __name__ == '__main__':
	import sys
	args = sys.argv[1:]
	with Pool() as pool:
		for r in pool.imap_unordered(load, args):
			print(r)

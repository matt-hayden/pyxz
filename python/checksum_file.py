#!/usr/bin/env python3
import re


class CheckSumFileException(Exception):
	pass
#
class CheckSumLine:
	str_format = "None"
	def __init__(self, n, filename):
		self.checksum, self.filename = n, filename
	def __str__(self):
		return self.str_format.format(self.checksum, self.filename)
	def __eq__(self, other):
		return self.checksum == other.checksum
	def __lt__(self, other):
		return self.checksum < other.checksum
class BinaryCheckSumLine(CheckSumLine):
	str_format = "{:064x} *{}"
	def __repr__(self):
		return "BinaryCheckSumLine({}, {})".format(self.checksum, self.filename)
class TextCheckSumLine(CheckSumLine):
	str_format = "{:064x} {}"
	def __repr__(self):
		return "TextCheckSumLine({}, {})".format(self.checksum, self.filename)
def parse(line, regex = re.compile(r'([0-9A-F]{32,64})\s+([*]?)(.+)', re.IGNORECASE), base=16):
	m = regex.match(line)
	if m:
		text, isbin, filename = m.groups()
		if isbin == '*':
			return BinaryCheckSumLine(int(text, base), filename)
		elif isbin == '':
			return TextCheckSumLine(int(text, base), filename)
		else:
			raise CheckSumFileException()
	else:
		raise CheckSumFileException()
#
def checksum_file(filename):
	with open(filename) as fin:
		for line in fin:
			yield parse(line.rstrip())
if __name__ == '__main__':
	import sys
	for arg in sys.argv[1:]:
		for obj in checksum_file(arg):
			print(obj.binary, obj.filename)
			print(obj)
#

#!/usr/bin/env python3
""" Very simple spell checker

	Usage:
		sc [-q] <word>
		sc (-h | --help)

	Options:
		-h, --help		Show this help
		-q, --quiet		Exit status indicates whether arg is misspelled
"""
from collections import Counter
import subprocess
import sys

from docopt import docopt
import enchant

def define(word):
	"""
	TODO: try to use wordnik for definitions
	"""
	return

###
if sys.stderr.isatty():
	def DEBUG(*args, **kwargs):
		pass
else:
	def DEBUG(*args, **kwargs):
		print("DEBUG:", *args, file=sys.stderr)
###

speller = enchant.Dict()
DEBUG("Locale", speller.tag)
DEBUG("Provider", speller.provider)
def suggest(*args, speller=speller, isunique=None):
	if not isunique:
		def isunique(word, forms):
			lc = word.lower()
			if word == lc:	return True
			if lc in forms:	return False
			return True
	s = speller.suggest(*args)
	return [f for f in s if isunique(f, s)]
###
if __name__ == '__main__':
	args = docopt(__doc__, version='sc 0.1')
	word = args['<word>']
	if speller.check(word):
		DEBUG(word, "correct")
	else:
		if args['-q']:	sys.exit(1)
		else:
			s = suggest(word)
			speak_process = subprocess.Popen(['say', s[0]])
			print(s)
			speak_process.wait()

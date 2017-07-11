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

import logging
logger = logging.getLogger(__name__)
debug, info, warning, error, panic = logging.debug, logging.info, logging.warning, logging.error, logging.critical

import enchant

def define(word):
	"""
	TODO: try to use wordnik for definitions
	"""
	return

speller = enchant.Dict()
debug("Locale", speller.tag)
debug("Provider", speller.provider)

def suggest(*args, speller=speller, isunique=None):
	if not isunique:
		def isunique(word, forms):
			lc = word.lower()
			if word == lc:	return True
			if lc in forms:	return False
			return True
	s = speller.suggest(*args)
	return [f for f in s if isunique(f, s)]
#
def get_sayer(phrase):
	def say(phrase):
		(yield)
		speak_process = subprocess.Popen(['say', phrase])
		(yield)
		speak_process.wait()
	next(say)
	return say
#
def check(word, quiet=False, sound=True, **kwargs):
	if speller.check(word):
		debug("{}: correct".format(word))
		return True
	else:
		if not quiet:
			s = suggest(word)
			if sound:
				say=get_sayer(s[0])()
				print(s)
				say.send()
			else:
				print(s)
if __name__ == '__main__':
	from docopt import docopt

	kwargs = docopt(__doc__, version='sc 0.11')
	word = kwargs.pop('<word>')
	options = { 'quiet': kwargs.pop('--quiet') }
	sys.exit(not check(word, **options))

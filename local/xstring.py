#! /usr/bin/env python
import itertools
from operator import mul
import string

def get_character_class_map(case_sensitive=False, numbers_are_hex=False):
	classes = []
	a = classes.append
	if numbers_are_hex:
		# ABCDEF and abcdef will be found as numbers before they're found as letters!
		a(string.hexdigits)
	else:
		a(string.digits)
	if case_sensitive:
		a(string.ascii_lowercase)
		a(string.ascii_uppercase)
	else:
		a(string.ascii_letters)
	classes += [string.punctuation, string.whitespace]
	return { c:n for n, c in enumerate(classes, start=256) }
def get_character_class(c, default=-1, class_map=get_character_class_map()):
	for char_class, n in class_map.iteritems():
		if c in char_class: return n
	return default
def custom_character_distance(c1, c2):
	if c1 == c2: return 0
	cl1, cl2 = get_character_class(c1), get_character_class(c2) # these are numbers
	if cl1 == cl2:
		if cl1 in (get_character_class('_'), get_character_class(' '), get_character_class('\0')):
			s = 255
		else:
			s = ord(c1) - ord(c2)
		if -1 <= s <= 1: return 0.1
		else:
			d = c1+c2
			if d in ('09', '90'): return 0.1
			elif d in ('0A', 'A0', '0F', 'F0'): return 0.1 # this is only true when hexdigits contain 0 and F
		return 0.5
	return 1
#
def _string_differences(s1, s2, ignore_prefix=string.punctuation+string.whitespace, ignore_suffix='', distance=custom_character_distance, fillvalue='0'):
	if not ignore_suffix:
		ignore_suffix = ignore_prefix
	if ignore_prefix:
		while s1[0] in ignore_prefix:
			s1 = s1[1:]
		while s2[0] in ignore_prefix:
			s2 = s2[1:]
	if ignore_suffix:
		while s1[-1] in ignore_suffix:
			s1 = s1[:-1]
		while s2[-1] in ignore_suffix:
			s2 = s2[:-1]
	shorter, longer = sorted([s1, s2], key=len)
	for c1, c2 in itertools.izip(shorter, longer):
		yield distance(c1, c2)
	offset = len(longer) - len(shorter)
	if offset:
		if fillvalue:
			shorter_fill = fillvalue*offset
		else:
			fillvalue = '_'
			shorter_fill = fillvalue*(offset-len(shorter))+shorter[-offset:]
		assert len(shorter_fill) == offset
		for c1, c2 in itertools.izip(shorter_fill, longer[-offset:]):
			yield distance(c1, c2)
#
def string_differences(*args, **kwargs):
	return list(_string_differences(*args, **kwargs))
def strings_differ(s1, s2, threshold=1.0/3, difference=string_differences):
	d = difference(s1, s2)
	if not d: return 0
	func = range(len(d), 0, -1)
	denom = sum(func)
	return sum(map(mul, func, d))/denom > threshold
#
def get_all_string_differences(strings, difference=string_differences):
	def key((s1, s2, d)):
		return d, s1, s2
	results = []
	a = results.append
	prev = strings.pop()
	while strings:
		for this in strings:
			a((prev, this, difference(this, prev)))
		prev = strings.pop() # last element falls through
	results.sort(key=key)
	return results
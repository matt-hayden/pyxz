#!env python
from collections import defaultdict
import csv
import os.path

from keycodes import AquacraftKeycode, Keycode

def is_comment(line):
	if not line.strip(): return True
	if line.startswith('#'): return True
	if line.startswith(';'): return True
	return None

###
### BEGIN GLOBALS
###
module_dirname, module_basename = os.path.split(__file__)
types_filename = os.path.join(module_dirname, 'KeycodeTypes.tab')
tags_filename = os.path.join(module_dirname, 'TagsByKeycodeRange.tab')

#keycode_types = { s[0].upper(): s for s in ['Agricultural', 'Commercial', 'Irrigation', 'Multi-family Residential', 'Single-Family Residence']}
#keycode_types['N'] = 'Institutional'
#keycode_types['X'] = None

#with open(types_filename, 'Ur') as fi:
#	reader = csv.reader((line for line in fi if not is_comment(line)), dialect='excel-tab')
#	keycode_types = {v:k for k,v in reader}

keycode_types = {
	AquacraftKeycode.AGRICULTURAL:	'Agricultural',
	AquacraftKeycode.COMMERCIAL:	'Commercial',
	AquacraftKeycode.IRRIGATION:	'Irrigation',
	AquacraftKeycode.MULTIFAMILY:	'Multi-family Residential',
	AquacraftKeycode.INSTITUTIONAL:	'Institutional',
	AquacraftKeycode.SINGLEFAMILY:	'Single-Family Residence',
	'X':							'<testing>' }

tags_by_keycode = defaultdict(set)
with open(tags_filename, 'Ur') as fi:
	reader = csv.reader((line for line in fi if not is_comment(line)), dialect='excel-tab')
	for tag, begin, end in reader:
		for k in Keycode(begin, end) if end else Keycode(begin):
			tags_by_keycode[k].add(tag)
###
### END GLOBALS
###

def get_keycode_type(k):
	"""
	This works for any valid keycode, even if never assigned nor used:
	>>> get_keycode_type('09S100')
	'Single-Family Residence'
	"""
	if not isinstance(k, AquacraftKeycode):
		k = Keycode(k)
	return keycode_types[k.site_type_code]
def get_tags_for_keycode(k):
	"""
	The client and site are returned in no particular order:
	>>> get_tags_for_keycode('10S401')
	set(['Single-Family Residence', 'Albuquerque', 'ABCWUA'])
	
	Some keycodes are unused or left undefined:
	>>> get_tags_for_keycode('10S130')
	set(['<unknown>', 'Single-Family Residence'])
	
	Even weirder, some keycodes contain even less information, even though
	they're valid:
	>>> get_tags_for_keycode('09X100')
	set(['<unknown>', '<testing>'])
	"""
	if not isinstance(k, AquacraftKeycode):
		k = Keycode(k)
	t = tags_by_keycode[k] or set(['<unknown>'])
	t.add(get_keycode_type(k))
	return t
if __name__ == '__main__':
	from collections import Counter
	import doctest
	
	from local.flatten import flatten
	
	doctest.testmod()
	print "Recognized site use types in", types_filename
	for k,v in sorted(keycode_types.iteritems()):
		print k+"="+v
	print
	print "Recognized tags: (see {} for designations)".format(tags_filename)
	c = Counter(flatten(get_tags_for_keycode(k) for k in tags_by_keycode))
	for k, v in sorted(c.iteritems(), key=lambda f:f[-1], reverse=True):
		print "{:5d} {}".format(v, k)
	print "Note: since lookups are cached, '<unknown>' and '<testing>' are NOT unusual."
#
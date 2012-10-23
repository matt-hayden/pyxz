#!env python
import csv
try:
	from decimal import Decimal
	parse_number_format = Decimal
except ImportError:
	parse_number_format = float

def parse_number(s, format=parse_number_format):
	if '%' in s:
		return parse_number(s.replace('%', '', 1))/format(100.0)
	return format(s)

def explode_table(fileobj, parser = parse_number):
	elements = []
	with fileobj as fi:
		cr = csv.reader(fi, delimiter='\t')
		cheader = cr.next()
		cornerlabel = cheader.pop(0)
		for row in cr:
			if row:
				sidelabel = row.pop(0)
				for toplabel, val in zip(cheader, row):
					elements.append((toplabel+sidelabel, parser(val)))
	return cornerlabel, elements
def print_table(filename, show_corner = False, sort_key=lambda x: x[1], sort_reverse=True):
	name, elements = explode_table(open(filename))
	if sort_key:
		elements.sort(key=sort_key, reverse=sort_reverse)
	if show_corner:
		print name
	for label, val in elements:
		print label, val
#
print_table('my-frequencies.tab', show_corner=True)
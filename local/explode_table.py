#!env python
import csv
from os.path import exists

try:
	from decimal import Decimal
	parse_number_formatter = Decimal
except ImportError:
	parse_number_formatter = float
#
class FileArgument: # abstract
	def load_file(self, filename):
		self.filename = filename
		self.fileobj = open(filename)
	def __init__(self, f):
		try:
			if exists(f):
				self.load_file(f)
		except:
			self.fileobj = f
class TableExploder: # abstract
	def get_elements(self):
		for toplabel, elements in self.get_rows():
			for sidelabel, val in elements:
				yield (toplabel+sidelabel, self.parser(val))
	__iter__ = get_elements
class CSVTableExploder(FileArgument, TableExploder): # abstract, should be subclassed
	def get_rows(self):
		with self.fileobj as fi:
			cr = csv.reader(fi, delimiter=self.delimiter)
			cheader = cr.next()
			self.cornerlabel = cheader.pop(0)
			for row in cr:
				if row:
					sidelabel = row.pop(0)
					yield (sidelabel, zip(cheader, row))

class explode_table(CSVTableExploder):
	delimiter='\t'
	formatter=parse_number_formatter
	def parser(self, s):
		if '%' in s:
			return self.formatter(s.replace('%', '', 1))/self.formatter(100.0)
		return self.formatter(s)
	def print_table(self, show_corner = False, sort_key=lambda x: x[1], sort_reverse=True):
		elements = [ (n, l) for n, l in self.get_elements() ]
		if sort_key:
			elements.sort(key=sort_key, reverse=sort_reverse)
		if show_corner:
			print self.cornerlabel
		for n, l in elements:
			print n,l
		
if __name__ == '__main__':
	explode_table('my-frequencies.tab').print_table(show_corner = True)
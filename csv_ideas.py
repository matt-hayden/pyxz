#!env python
from ast import literal_eval
from collections import Counter
import csv
from datetime import datetime
import dateutil.parser
#from itertools import groupby
import os.path
import sys

args = sys.argv[1:] or ['L-07596S011_pilot home 1.txt', 'L-07638S039.TXT', '13s134h.csv']
#
def detect_conversion_type(text, timestamp_parser=dateutil.parser.parse):
	try:
		stext = text.strip()
	except:
		return 'unknown'
	if stext == '':
		return 'NULL'
	if stext.isdigit():
		return 'int'
	try:
		v = float(stext)
		return 'float'
	except: pass
	try:
		ts = timestamp_parser(stext)
		return 'datetime'
	except: pass
	try:
		r = literal_eval(stext)
		rt = type(r).__name__
		if rt: return rt
	except: pass
	return 'string'
#
def collector():
	stored = []
	try:
		content = (yield stored)
		stored.append(content)
	finally:
		print "Collected:", content

def collect_csv_field_types(rows, 
				typer=detect_conversion_type,
				results_coroutine=collector()):
	nfield_distribution = Counter()
	type_distribution = Counter()
	try:
		for row in rows:
			nfield_distribution[len(row)] += 1
			field_types = [typer(_) for _ in row] or ['NULL']
			type_distribution[','.join(field_types)] += 1
			yield row
	finally:
		results_coroutine.next()
		results_coroutine.send(type_distribution)
#
def csv_summarizer(filename, dialect=None, max_rows=100):
	dirname, basename = os.path.split(filename)
	filepart, fileext = os.path.splitext(basename)
	size = os.path.getsize(filename)
	if not size:
		print "'{}' is empty".format(basename)
		return
	nfield_distribution = Counter()
	type_distribution = Counter()
	with open(filename, 'rb') as csvfile:
		if not dialect:
			ext = fileext.upper()
			if ext == '.CSV':
				dialect = 'excel'
			elif ext in ['.TAB', '.TSV']:
				dialect = 'excel-tab'
			else:
				try:
					first_block = csvfile.read(1024)
					dialect = csv.Sniffer().sniff(first_block)
				except Exception as e:
					print "'{}' is not openable as a CSV: {}".format(basename, e)
					print
					return
				finally:
					csvfile.seek(0)
		if dialect:
			reader = csv.reader(csvfile, dialect=dialect)
		else:
			reader = csv.reader(csvfile)
		numbered_reader = enumerate(reader, start=1)
		#
		header = None
		rownum, first_row = numbered_reader.next()
		if len(first_row) == 0:
			nfield_distribution[0] += 1
			type_distribution['NULL'] += 1
		else:
			first_row_field_types = [detect_conversion_type(_) for _ in first_row]
			if len(first_row) == 1:
				if first_row_field_types == ['string']:
					header = first_row
			elif set(first_row_field_types)-set(['string']): # if there's more than strings on this row
				nfield_distribution[len(first_row)] += 1
				type_distribution[','.join(first_row_field_types)] += 1
			else:
				rownum, second_row = numbered_reader.next()
				if len(second_row):
					second_row_field_types = [detect_conversion_type(_) for _ in second_row]
					if set(second_row_field_types)-set(['string', 'NULL']): # if there's more than strings and NULLs on this row
						header = first_row
					nfield_distribution[len(second_row)] += 1
					type_distribution[','.join(second_row_field_types)] += 1
				else: # hmm
					nfield_distribution[0] += 1
					type_distribution['NULL'] += 1
		#
		print header
		print first_row, first_row_field_types
#		print second_row, second_row_field_types
		#
		for rownum, row in numbered_reader:
			if rownum > max_rows: break
			try:
				nfields = len(row)
			except ValueError as e:
				print >>sys.stderr, row, "not recognized: {}".format(e)
			else:
				nfield_distribution[nfields] += 1
			field_types = [detect_conversion_type(_) for _ in row]
			type_distribution[','.join(field_types)] += 1
		nrows = rownum
	if len(nfield_distribution) == 1:
		(nfields, nrows), = nfield_distribution.most_common()
		print "'{}' is a {:,} byte CSV with a consistent {} fields on first {:,} rows".format(basename, size, nfields, nrows)
		if header:
			print "The likeliest header is {}".format(header)
	else:
		min_fields, max_fields = min(nfield_distribution), max(nfield_distribution)
		print "'{}' is {:,} bytes".format(basename, size)
		print "On first {:,} rows, number of fields per line varies between {} and {}".format(nrows, min_fields, max_fields)
		if header:
			if len(header) == max_fields:
				print "The likeliest header is {}".format(header)
			else:
				print "At least one row has more fields than the first row"
	for field_types, nrows in type_distribution.most_common():
		print "{} rows are {}".format(nrows, field_types)
	print
#
for arg in args:
	with open(arg, 'rb') as csvfile:
		reader = csv.reader(csvfile)
		coroutine = collect_csv_field_types(reader)
#		print coroutine.next()
		for rownum, row in enumerate(coroutine, start=1):
			if rownum > 27: break
			print rownum, row
		print coroutine.next()
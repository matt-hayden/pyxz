#!env python
import csv
from datetime import date, datetime
import os.path

default_filename = 'holidays.tab'
dirname, basename = os.path.split(__file__)

def convert_date(text, format = '%Y-%m-%d'):
	return datetime.strptime(text, format).date()

def get_holidays(start=None, end=None, filename=None):
	filename = filename or os.path.join(dirname, default_filename)
	if type(start) == int:
		start = date(start,1,1)
	if type(end) == int:
		end = date(end,1,1)
	with open(filename) as fi:
		r=csv.reader(fi, dialect='excel-tab')
		if start or end:
			for datetext, nametext in r:
				d = convert_date(datetext)
				if start and (d <= start): continue
				if end and (end <= d): continue
				yield d, nametext.title()
		else:
			for datetext, nametext in r:
				yield convert_date(datetext), nametext.title()
#
holidays = { d:n for d,n in get_holidays() }

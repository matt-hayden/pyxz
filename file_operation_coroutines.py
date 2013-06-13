#!env python
import csv
from logging import debug, info, warning, error, critical

"""
Example:
w = simple_file_writing_coroutine('foo')
w.next()
w.send("something")

The coroutine exits with Python
"""
def simple_file_writing_coroutine(filename, mode='wb', line_limit=10**7):
	with open(filename, mode=mode) as fo:
		try:
			for iteration in xrange(line_limit):
				### remember to wrap (yield) in high-velocity protective parenthesis
				content = str((yield))
				debug("Iteration {}: {}".format(iteration, content))
				fo.write(content if content.endswith('\n') else content+'\n')
		except GeneratorExit:
			debug("Last was iteration {}-1: {}".format(iteration, content))
def csv_file_writing_coroutine(filename, mode='wb', row_limit=10**7, **kwargs):
	with open(filename, mode=mode) as fo:
		writer = csv.writer(fo, **kwargs)
		try:
			for iteration in xrange(row_limit):
				content = (yield)
				debug("Iteration {}: {}".format(iteration, content))
				writer.writerow(content)
		except GeneratorExit:
			debug("Last was iteration {}-1: {}".format(iteration, content))
#
#!env python
"""
DocString description goes here.
"""
#from __future__ import with_statement # must be first for python 2.5 or older

# these are the minimum imports for the stub:
import logging
from multiprocessing import Pool, freeze_support, get_logger
from optparse import OptionParser, OptParseError
import os.path
import sys

from logging import debug, info, warning, error, critical

usage = '%prog [options] input [input...]'
__version__ = 0.0

###
# BEGIN Example
# my_hourglass processes individual files. In this example, simply calculating
# the size and passing some events to the logging module.
# my_hourglass wraps the code for parallel execution. Any exceptions thrown
# will derail any future processes. It returns an object consumed by
# my_callback. In this case, a simple state tuple.
###
from datetime import datetime
from random import random
from time import sleep

def my_hourglass(filename, **kwargs):
	"""
	Logging is independent of the logger used in main(), in this case separated
	by filename. 
	"""
	started = datetime.now()
	dirname, basename = os.path.split(filename)
	logfile = kwargs.pop('logfile', basename+'.log')
	logging.basicConfig(filename=logfile,		#
						filemode='w',			# overwrite existing log file
						level=logging.DEBUG if __debug__ else logging.WARNING)
	
	size = os.path.getsize(filename)
	debug("Before sleep")
	sleep(0.2*random())
	debug("After sleep")
	
	logging.shutdown()
	return (datetime.now()-started, filename, "done", size)
def my_callback(result, stderr=sys.stderr, **kwargs):
	duration, filename, state, size = result
	if state == 'done':
		print duration, "{} = {} bytes".format(filename, size)
	else:
		print >> stderr, "Problem with {}: {}".format(filename, state)
###
# END Example
###

def main(*args):
#	if not args: args = sys.argv[1:]
	options, args = get_parser({'log_level':		logging.DEBUG if __debug__ else logging.WARNING,
								'has_input':		True,
								'open_mode':		'rU',
								'input_filenames':	[],
								'has_output':		False,
								'allow_overwrite':	False,
								'save_mode':		'w+',
								'tempfile':			None,
								'timeout':			60*60,
								'hourglass':		my_hourglass,
								'callback':			my_callback
							   })
	log_level = options.log_level
	if log_level < logging.ERROR: log_level += -10*(options.verbose or 0)
	if options.logfile:
		logging.basicConfig(filename=options.logfile,
							level=log_level)
	else:
		logging.basicConfig(level=log_level)
	logging.captureWarnings(True)
	
	if hasattr(sys, 'frozen'): # has no __file__
		dirname, basename = os.path.split(sys.argv[0])
		debug("{} version {} started".format(basename, __version__))
	else: # __file__ contains script filename
		debug("{} version {} started".format(__file__, __version__))
	if options.has_input:
		options.input_filenames.extend(args)
		if options.list_of_input_filenames:
			if options.list_of_input_filenames == '-':
				options.input_filenames.extend(_.rstrip() for _ in sys.stdin)
			else:
				with open(options.list_of_input_filenames, options.open_mode) as fi:
					options.input_filenames.extend(_.rstrip() for _ in fi)
		for ifn in options.input_filenames:
#			assert (os.path.isfile(ifn) and os.path.getsize(ifn)) or ifn in ('-')
			debug("Input:"+ifn)
	if options.has_output:
		info("Output:"+options.output_filename)
#	if options.tempfile is not None:
#		debug("Using temporary file {}".format(tempfile))
	try:
		hourglass, callback = options.hourglass, options.callback
		mp = Pool()
		for result in mp.imap_unordered(hourglass, options.input_filenames):
			callback(result)
	except KeyboardInterrupt:
		warning("Ended with user intervention")
	finally:
		logging.shutdown()
def get_parser(defaults = {}, **kwargs):
	defaults.update(kwargs)
	parser=OptionParser(usage=usage,
						description=__doc__,
						version=__version__,
						conflict_handler='resolve')
	# parser.add_option() defaults to (action='store', type='string')
	'''
	Command-line
	'''
	parser.add_option('-v', '--verbose',
					  action='count', dest='verbose',
					  help="Show more detail (-vv for even more)")
	parser.add_option('-q', '--quiet',
					  action='store_const', dest='log_level', const=logging.CRITICAL,
					  help="Show less detail")
	'''
	Input files
	'''
	parser.add_option('--filein',
					  dest='input_filenames', metavar='FILE', action='append',
					  help='Multiple occurrances allowed for multiple input files.')
	parser.add_option('-@', '--file-list',
					  dest='list_of_input_filenames', metavar='FILE',
					  help='Newline-separated list of input files. - implies stdin')
	'''
	Output file and options
	'''
	parser.add_option('--fileout',
					  dest='output_filename', metavar='FILE',
					  help='specify (only one) output file')
	parser.add_option('-a', '--append',
					  action='store_const', dest='save_mode', const='a',
					  help="Append to output file instead of write")
	parser.add_option('-f', '--overwrite',
					  action='store_true', dest='allow_overwrite',
					  help='Overwrite output file')
	parser.add_option('-t', '--create-temp',
					  action='store_true', dest='create_temp_output',
					  help="Handle output into a temp file, then move into place.")
	'''
	Advanced options
	'''
	parser.add_option('--logfile',
					  dest='logfile', metavar='FILE',
					  help="Log output to a local file.")
	parser.add_option('--log-level', action='store',
					  dest='log_level', type='int',
					  help="See logging module documentation for different log levels.")
	parser.add_option('--tempfile',
					  dest='temp', metavar='FILE',
					  help="Use the specified file as a place to dump output before moving it over the output file.")
	parser.add_option('-t', '--timeout',
					  dest='timeout', type='int',
					  help="Number of seconds to run")
	if defaults: parser.set_defaults(**defaults)
	return parser.parse_args()
###
if __name__ == '__main__':
	freeze_support() # for cx_freeze
	sys.exit(main() or 0)

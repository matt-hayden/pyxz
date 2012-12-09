import logging
import os.path
from TraceWizard5 import open_file

logger = logging.getLogger(__package__)
logger.setLevel(logging.DEBUG)

tempdir = os.path.expandvars('%TEMP%\example-traces')
files = [os.path.join(tempdir, fn) for fn in '12S704.twdb', '12S704.csv', '67096.tdb', '67096.MDB']

if True:
	print
	print "Loading just headers:"
	
	f = open_file(files[0], load_flows = False)
	print f
	#f.parse_ARFF_header()
	#print f
	
	f = open_file(files[1], load_flows = False)
	print f
	#f.parse_CSV_header()
	#print f
	
	f = open_file(files[2], load_flows = False)
	print f
	
	f = open_file(files[3], load_flows = False)
	print f

if False:
	print
	print "Loading whole files:"
	for fn in files:
		print open_file(fn)
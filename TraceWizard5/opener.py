import os.path

from TraceWizard4.MeterMaster3_File import MeterMaster3_MDB
from TraceWizard4.TraceWizard4_File import TraceWizard4_File
from MeterMaster4_parser import MeterMaster4_CSV
from TraceWizard5_File import TraceWizard5_File

def open_file(filename):
	ext = os.path.splitext(filename)[-1]
	ext = ext.upper()
	if ext == '.TWDB':
		return TraceWizard5_File(filename)
	elif ext == '.CSV':
		return MeterMaster4_CSV(filename)
	elif ext == '.TDB':
		return TraceWizard4_File(filename)
	elif ext == '.MDB':
		return MeterMaster3_MDB(filename)
if __name__ == '__main__':
	tempdir=os.path.expandvars('%TEMP%\example-traces')
	for fn in [ os.path.join(tempdir, f) for f in "01_07nov2011_16nov2011.twdb 09_22oct2011_append_21dec2011.twdb 12S704.csv 12S704.twdb 67096-2003.MDB 67096.MDB 67096.tdb".split() ]:
		print fn, "=", open_file(fn)
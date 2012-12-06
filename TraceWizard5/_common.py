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
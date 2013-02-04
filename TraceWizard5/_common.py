import os.path

from TraceWizard4.MM import MeterMaster3_MDB
from TraceWizard4.file import TraceWizard4_import
from TraceWizard5.MM import MeterMaster4_CSV
from TraceWizard5.file import TraceWizard5_import

def open_file(filename, *args, **kwargs):
	ext = os.path.splitext(filename)[-1]
	ext = ext.upper()
	format = kwargs.pop('format', None)
	if format == 'TraceWizard5' or ext == '.TWDB':
		return TraceWizard5_import(filename, *args, **kwargs)
	elif format == 'MeterMaster4' or ext in ('.CSV', '.ZIP'):
		return MeterMaster4_CSV(filename, *args, **kwargs)
	elif format == 'TraceWizard4' or ext == '.TDB':
		return TraceWizard4_import(filename, *args, **kwargs)
	elif format == 'MeterMaster3' or ext == '.MDB':
		return MeterMaster3_MDB(filename, *args, **kwargs)
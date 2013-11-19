#!env python
# Z:\Projects\Santa_Clarita\weather
# acceleration possible with packages numexpr and bottleneck
# Excel writing possible with xlwt
import os
import os.path

import pandas as pd

#from local.xglob import glob
from local.sanitize import Excel_sheet_name_sanitize

CIMIS_params	=	{ 'parse_dates': 'Date', 'index_col': 'Date', 'na_values': '--' }
NCDC_params		=	{ 'parse_dates': 'DATE', 'index_col': 'DATE', 'na_values': ['9999', '-9999'] }

#
def CIMIS_import(input_files):
	df = pd.read_csv(input_files.pop(0), **CIMIS_params)
	for nf in input_files:
		nt = pd.read_csv(nf, **CIMIS_params)
		df = df.append(nt)
	#
	#df.dropna(how='all') # days missing all values
	return df
#
def NCDC_import(input_files):
	df = pd.read_csv(input_files.pop(0), **NCDC_params)
	for nf in input_files:
		nt = pd.read_csv(nf, **NCDC_params)
		df = df.append(nt)
	#
	#df.dropna(how='all') # days missing all values
	df['PRCP'] /= 10.0 # convert to mm
	df['MDPR'] /= 10.0 # convert to mm
	
	df['TMAX'] /= 10.0 # convert to Celsius
	df['TMIN'] /= 10.0 # convert to Celsius
	
	df['AWND'] /= 10.0 # convert to m/s
	df['WSF2'] /= 10.0 # convert to m/s
	df['WSF5'] /= 10.0 # convert to m/s
	return df
#
def export(df, output_filename, key):
	headers = df.columns
	df.columns = [ t.decode('ascii', 'ignore') for t in headers ]
	stations = df[key].unique()
	if len(stations) == 1:
		sheet_name = Excel_sheet_name_sanitize(stations[0])
		df.to_excel(output_filenamename, sheet_name)
	else:
		# Since pandas 0.13, this is context aware
		fo=pd.ExcelWriter(output_filename)
		for station in stations:
			sheet_name = Excel_sheet_name_sanitize(station)
			df[df[key]==station].to_excel(fo, sheet_name)
		fo.save()
		del fo
#
def CIMIS_to_Excel(input_files, output_filename='cimis.xlsx', key=['Region', 'Station', 'Stn Id']):
	df = CIMIS_import(input_files)
	print "Number of observations by station:"
	print df.groupby(key).count()
	export(df, output_filename, key='Station')
#
def NCDC_to_Excel(input_files, output_filename='ncdc.xlsx', key='STATION'):
	df = NCDC_import(input_files)
	print "Number of observations by station:"
	print df.groupby(key).count()
	export(df, output_filename, key='STATION')
#
import sys
args = sys.argv[1:]
input_files = args
print "Reading input files", input_files
#CIMIS_to_Excel(args)
df = NCDC_import(input_files)
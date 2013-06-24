#!env python
import logging
logging.basicConfig(level=logging.DEBUG, filename='aquacue_test.log')

from collections import Counter, defaultdict, namedtuple
from datetime import datetime, timedelta
from logging import debug, info, warning, error, critical
import sys
from urllib import urlencode

import pandas as pd

from TraceWizard4.MDB_File import MDB_File

base_url = "https://aquacue.net/api/data"
params = { 'service_uuid':	2616903987244451787,
		   'aggregate':		'hourly' }
hourly_tablename = 'tblHourlyReads_'+str(params['service_uuid'])
daily_tablename = 'tblDailyReads_'+str(params['service_uuid'])

today = datetime.now().date()
yesterday = today - timedelta(days=1)

try:
	with MDB_File('proto.mdb') as db:
		with db.execute("select max(EndDate) from {};".format(hourly_tablename)) as cursor:
			latest_timestamp, = cursor.fetchone()
	last_day = latest_timestamp.date() + timedelta(days=1)
except:
	info("No latest timestamp")
	last_day = datetime(2013,03,21).date()
debug("Last update was apparently {}".format(last_day))
if yesterday <= last_day:
	sys.exit("Last update was {}, please be patient!".format(last_day))

params['start_date']	= last_day.strftime('%Y-%m-%d') if last_day else ''
params['end_date']		= yesterday.strftime('%Y-%m-%d')
url = base_url+'?'+urlencode(params)
debug("Using URL {}".format(url))

### to retrieve without pandas:
#debug("POST string: {}".format(urlencode(params)))
#response = urllib2.urlopen(base_url+'?'+urlencode(params))
#debug("received url {}".format(response.geturl()))
#debug("received headers {}".format(response.info()))
#debug("received return code {}".format(response.getcode()))

### to read without pandas
#reader = csv.reader(response, dialect='excel')
#table_headers = [_.strip() for _ in reader.next()]
#factory = namedtuple('AquacueRow', table_headers)
#table = (factory(*record) for record in reader)

unit_conversion = pd.Series({'GAL': 1.0, 'CF': 7.48})

table = pd.read_csv(url, sep=r',\s*', parse_dates=['START_DATE', 'END_DATE'], index_col=['END_DATE'])
label_parts = []
#for colname in ['SERVICE_UUID']:
#	vc = table[colname].value_counts()
#	if len(vc)<=1:
#		label_parts.append(vc.index[0])
#label = '_'.join(str(_) for _ in label_parts)
table['conversion_factor'] = table['UNIT'].map(unit_conversion)
slice = table.reindex(columns=['VALUE', 'conversion_factor'])

with MDB_File('proto.mdb', nocommit=False) as db:
	hourly_writer = db.get_create_coroutine(hourly_tablename, 'EndDate Reading ConversionFactor', field_types='DATETIME DOUBLE DOUBLE')
	daily_writer = db.get_create_coroutine(daily_tablename, 'EndDate Reading ConversionFactor', field_types='DATETIME DOUBLE DOUBLE')
	hourly_writer.next() # initialize
	daily_writer.next()
	for row in slice.itertuples():
		try:
			hourly_writer.send(row)
		except Exception as e:
			print row, [type(_) for _ in row]
			raise e
	for row in slice.resample('1D', how='sum').itertuples():
		daily_writer.send(row)
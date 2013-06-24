#!env python
import logging
logging.basicConfig(level=logging.DEBUG) # , filename='aquacue_test.log')
###

from datetime import datetime, timedelta
from logging import debug, info, warning, error, critical

from TraceWizard4.MDB_File import MDB_File

from Aquacue_update import get_Aquacue_update

horizon = datetime(2013,03,21).date()

def Aquacue_MDB_updater(db_filename,
						params,
						hourly_tablename=None,
						daily_tablename=None):
	today = datetime.now().date()
	yesterday = today - timedelta(days=1)
	
	if 'service_uuid' in params:
		label = str(params['service_uuid'])
		hourly_tablename = hourly_tablename or 'tblHourlyReads_'+label
		daily_tablename = daily_tablename or 'tblDailyReads_'+label
	with MDB_File(db_filename, nocommit=False) as db:
		try:
			with db.execute("select max(EndDate) from {};".format(hourly_tablename)) as cursor:
				latest_timestamp, = cursor.fetchone()
			last_day = latest_timestamp.date() + timedelta(days=1)
		except:
			info("No latest timestamp")
			last_day = horizon
		debug("Last update was apparently {}".format(last_day))
		### TODO: 
		if yesterday <= last_day:
			raise NotImplementedError("Last update was {}, please be patient!".format(last_day))
		###
		hourly_writer = db.get_create_coroutine(hourly_tablename, 'EndDate Reading ConversionFactor', field_types='DATETIME DOUBLE DOUBLE')
		daily_writer = db.get_create_coroutine(daily_tablename, 'EndDate Reading ConversionFactor', field_types='DATETIME DOUBLE DOUBLE')
		hourly_writer.next() # initialize
		daily_writer.next()
		aquacue_response = get_Aquacue_update(params=params, last_day=last_day)
		for row in aquacue_response.itertuples():
			hourly_writer.send(row)
		for row in aquacue_response.resample('1D', how='sum').itertuples():
			daily_writer.send(row)
if __name__ == '__main__':
	import sys
	params = { 'service_uuid':	2616903987244451787,
			   'aggregate':		'hourly' }
	Aquacue_MDB_updater('proto.mdb', params=params)
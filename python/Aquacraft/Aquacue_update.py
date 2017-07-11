#!env python
"""
https://aquacue.net/api/data?service_uuid=2616903987244451787&start_date=2013-03-21&aggregate=daily
https://aquacue.net/api/data?aggregate=hourly&service_uuid=2616903987244451787&start_date=2013-07-01&end_date=2013-07-15
"""
import base64
from datetime import datetime, timedelta
from logging import debug, info, warning, error, critical
from urllib import urlencode
import urllib2

import pandas as pd

passwords = urllib2.HTTPPasswordMgrWithDefaultRealm()

unit_conversion = pd.Series({'GAL': 1.0, 'CF': 7.48})

def get_Aquacue_update(params, last_day, base_url='https://aquacue.net/api/data'):
	global passwords
	today = datetime.now().date()
	yesterday = today - timedelta(days=1)
	
	base64string = base64.encodestring(':'.join(('aquacraft', 'aqua1aqua'))).strip()
	
	passwords.add_password(None, 'https://aquacue.net', 'aquacraft', 'aqua1aqua')
	handler = urllib2.HTTPBasicAuthHandler(passwords)
	opener = urllib2.build_opener(handler)
	
	# TODO: authentication
	debug("Authenticating:")
#	response = opener.open('https://aquacue.net/wave_api/1/info?service_uuid=2616903987244451787')
	req = urllib2.Request('https://aquacue.net/wave_api/1/info?service_uuid=2616903987244451787')
	req.add_header("Authorization", "Basic "+base64string)
	response = urllib2.urlopen(req)
	print response.read()
	return None
	# fetch
	if 'start_date' not in params:
		params['start_date']	= last_day.strftime('%Y-%m-%d') if last_day else ''
	if 'end_date' not in params:
		params['end_date']		= yesterday.strftime('%Y-%m-%d')
	url = base_url+'?'+urlencode(params)
	debug("Using URL {}".format(url))
	try:
		debug("Opening "+url)
		response = opener.open(url)
	except urllib2.HTTPError as e:
		error(str(e))
		return None
	try:
		table = pd.read_csv(url, sep=r',\s*', parse_dates=['START_DATE', 'END_DATE'], index_col=['END_DATE'])
	except Exception as e:
		print url, "broken:", e
		raise e
	label_parts = []
	#for colname in ['SERVICE_UUID']:
	#	vc = table[colname].value_counts()
	#	if len(vc)<=1:
	#		label_parts.append(vc.index[0])
	#label = '_'.join(str(_) for _ in label_parts)
	table['conversion_factor'] = table['UNIT'].map(unit_conversion)
	return table.reindex(columns=['VALUE', 'conversion_factor'])
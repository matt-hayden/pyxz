#!env python
from datetime import datetime, timedelta
from logging import debug, info, warning, error, critical
from urllib import urlencode

import pandas as pd

unit_conversion = pd.Series({'GAL': 1.0, 'CF': 7.48})

def get_Aquacue_update(params, last_day, base_url="https://aquacue.net/api/data"):
	today = datetime.now().date()
	yesterday = today - timedelta(days=1)
	if 'start_date' not in params:
		params['start_date']	= last_day.strftime('%Y-%m-%d') if last_day else ''
	if 'end_date' not in params:
		params['end_date']		= yesterday.strftime('%Y-%m-%d')
	url = base_url+'?'+urlencode(params)
	debug("Using URL {}".format(url))
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
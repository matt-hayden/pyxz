#from datetime import datetime

from . import *

def get_forecast_text(url):
	try:
		response = urllib2.urlopen(forecast_url)
		forecast_text = response.read()
	except:
		with open(forecast_url) as fi:
			forecast_text = fi.read()
	root = ET.fromstring(forecast_text)
	return root
def _get_txtforecasts(url=forecast_url, metric=False):
	root = get_forecast_text(url)
	days = root.findall('./forecast/txt_forecast/forecastdays/')
	for c in days:
		title = c.find('title').text
		text = c.find('fcttext_metric' if metric else 'fcttext').text
		yield (title, text)
def _get_simpleforecasts(url=forecast_url, temp_units='celsius', speed_units='mph'):
	root = get_forecast_text(url)
	days = root.findall('./forecast/simpleforecast/forecastdays/')
	for c in days:
		n = Namespace()
		n['date'] = dateutil.parser.parse(c.find('date/pretty').text)
		for m in ('low', 'high'):
			n[m] = c.find(m+'/'+temp_units).text
		for m in ('avewind', 'maxwind'):
			n[m] = c.find(m+'/'+speed_units).text
		n['conditions'] = c.find('conditions').text
		yield (n.pop('date', None), n)
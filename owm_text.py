#!env python
from datetime import datetime
from itertools import groupby
import json
from urllib2 import urlopen

from local.units import *

city_by_lat_lon_string = '''http://openweathermap.org/data/2.1/find/city?lat={lat}&lon={lon}&cnt={cnt}'''

conditions_by_lat_lon_string = '''http://openweathermap.org/data/2.1/find/city?lat={lat}&lon={lon}&cnt={cnt}'''
#conditions_by_lat_lon_string = '''http://openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}'''
forecast_by_lat_lon_string = '''http://openweathermap.org/data/2.1/forecast/city?lat={lat}&lon={lon}&cnt={cnt}'''
#forecast_by_lat_lon_string = '''http://openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}'''
url_for_icon_string = '''http://openweathermap.org/img/w/{icon}.png'''

def get_current_conditions(**kwargs):
	lat = kwargs.pop('latitude',None)
	if lat is None:
		lat = kwargs.pop('lat',None)
	lon = kwargs.pop('longitude',None)
	if lon is None:
		lon = kwargs.pop('lon',None)
	station_count = 1
	txt = urlopen(conditions_by_lat_lon_string.format(lat=lat, lon=lon, cnt=station_count))
	return json.load(txt)
def get_forecast(**kwargs):
	lat = kwargs.pop('latitude',None)
	if lat is None:
		lat = kwargs.pop('lat',None)
	lon = kwargs.pop('longitude',None)
	if lon is None:
		lon = kwargs.pop('lon',None)
	station_count = 1
	txt = urlopen(forecast_by_lat_lon_string.format(lat=lat, lon=lon, cnt=station_count))
	return json.load(txt)
#def get_forecast(id):
#	txt = urlopen(forecast_by_lat_lon_string.format(id=id))
#	return json.load(txt)
def parse_conditions(conditions, station = 0, **kwargs):
#	try:
#		m = conditions['message']
#	except:
#		print conditions
#		m = ''
#	if 'ERROR' in str(m).upper():
#		raise ValueError("Observation errored: {}".format(conditions))
	w = conditions['list'][station]
	return parse_forecast(w, **kwargs)
def parse_forecast(w, day = 0):
	d = {}
	if 'dt' in w:
		d['date'] = datetime.fromtimestamp(w['dt'])
	if 'name' in w:
		d['station name'] = w['name']
	if 'id' in w:
		d['station id'] = w['id']
	if 'clouds' in w:
		d['cloud cover'] = (w['clouds']['all'], '%')
	if 'main' in w:
		d['humidity'] = (w['main']['humidity'], '%')
		d['pressure'] = (w['main']['pressure'], 'mBar')
		d['temperature'] = (kelvin_to_celsius(w['main']['temp']), '*C')
		d['temperature range'] = ((kelvin_to_celsius(w['main']['temp_min']),
								   kelvin_to_celsius(w['main']['temp_max'])), '*C')
	if 'weather' in w:
		d['weather short description'] = w['weather'][day]['main']
		d['weather long description'] = w['weather'][day]['description']
		d['icon url'] = url_for_icon_string.format(icon = w['weather'][day]['icon'])
		# http://openweathermap.org/wiki/API/Weather_Condition_Codes
		# w['weather'][day]['id']
	if 'wind' in w:
		d['wind speed'] = (w['wind']['speed'], 'm/s', direction_name(w['wind']['deg']))
	if 'rain' in w:
		d['rain'] = (w['rain']['3h']/3.0, 'mm/hr')
	if 'snow' in w:
		d['snow'] = (w['snow']['3h']/3.0, 'mm/hr')
	return d
def generate_forecast(**kwargs):
	"""
	The first element is current conditions. Following elements are the default
	forecast.
	"""
	c = get_current_conditions(**kwargs)
	yield parse_conditions(c)
	for _ in get_forecast(**kwargs)['list']:
		yield parse_forecast(_)
#
if __name__ == '__main__':
#	c = get_forecast(lat=40, lon=-105.25)
#	c = get_current_conditions(lat=40, lon=-105.25)
	for gday, fs in groupby(generate_forecast(lat=40, lon=-105.25), lambda _: _['date'].date()):
		daily = list(fs)
		label = gday.strftime('%a %d')
		print label,
		print ''.join('{[0]:.0f}'.format(_['temperature']).center(8, '.') for _ in daily)
		print '-'*len(label), ' ',
		for gcond, fs in groupby(daily, lambda _: _['weather short description']):
			cdaily = list(fs)
			print gcond.center(8*len(cdaily)-2,'-')+' ',
		print
		print

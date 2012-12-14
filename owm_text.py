from datetime import datetime
import json
from math import sin, cos, pi, radians
from urllib2 import urlopen


def kelvin_to_celsius(k):
	return k-273.15
def celsius_to_fahrenheit(c):
	return 9*c/5+32
def kelvin_to_fahrenheit(k):
	return celsius_to_fahrenheit(kelvin_to_celsius(k))
def english_direction(angle, unit='degrees'):
	if unit == 'degrees':
		angle = radians(angle)
	angle %= 2*pi
	#
	n_to_s, w_to_e = cos(angle), sin(angle)
	if abs(n_to_s) < 0.382683432365:
		n_part = ""
	elif (n_to_s>0):
		n_part = "N"
	else:
		n_part = "S"
	#
	if abs(w_to_e) < 0.382683432365:
		w_part = ""
	elif (w_to_e>0):
		w_part = "W"
	else:
		w_part = "E"
	return n_part+w_part

conditions_by_lat_lon_string = '''http://openweathermap.org/data/2.1/find/city?lat={lat}&lon={lon}&cnt={cnt}'''
forecast_by_lat_lon_string = '''http://openweathermap.org/data/2.1/forecast/city?lat={lat}&lon={lon}&cnt={cnt}'''
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
def parse_conditions(conditions, station = 0, day = 0):
	assert "ERROR" not in conditions['message'].upper()
	w = conditions['list'][station]
	return parse_forecast(w, day)
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
		d['wind speed'] = (w['wind']['speed'], 'm/s', english_direction(w['wind']['deg']))
	if 'rain' in w:
		d['rain'] = (w['rain']['3h']/3, 'mm/hr')
	if 'snow' in w:
		d['snow'] = (w['snow']['3h']/3, 'mm/hr')
	return d
if __name__ == '__main__':
	from pprint import pprint
	#c = get_current_conditions(lat=40, lon=-105.25)
	c = get_forecast(lat=40, lon=-105.25)
	for fd in c['list']:
		f=parse_forecast(fd)
		print f['date'], "%3.0f %s" % f['temperature'], f['weather short description']

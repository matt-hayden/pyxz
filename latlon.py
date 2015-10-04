#! /usr/bin/env python2
"""
Resolve latitude/longitude from simple placenames. In the case of multiple
points returned from the web geocoder, the median is taken. It seems to work
best when ZIP is given.
If modifying the geocoder, note that geopy has slight implementation 
differences, see https://code.google.com/p/geopy/wiki/GettingStarted
"""
from logging import debug, info, warning, error, critical

from geopy import geocoders
from numpy import median

class LatLonException(Exception):
	pass

lat_lon_cache = {}
#gc = geocoders.GeoNames(format_string="%s, USA")
gc = geocoders.GoogleV3()
#
def decdeg2dms(dd):
	### http://stackoverflow.com/questions/2579535/how-to-convert-dd-to-dms-in-python
	negative = dd < 0
	dd = abs(dd)
	minutes,seconds = divmod(dd*3600,60)
	degrees,minutes = divmod(minutes,60)
	if negative:
		if degrees > 0:
			degrees = -degrees
		elif minutes > 0:
			minutes = -minutes
		else:
			seconds = -seconds
	return (degrees,minutes,seconds)

def fetch_lat_lon(loc, *args, **kwargs):
	sanity_check = kwargs.pop('sanity_check', True)
	#
	def sanity_checker(lat, lon, *args):
		if lat is None: return False
		if lon is None: return False
		if args: return False
		try:
			lat, lon = float(lat), float(lon)
		except:
			return False
		if not (0 <= lat <= 90): return False
		if not (-180 <= lon <= 180): return False
		return True
	#
	"""
	Result is a list of tuples like (place, (lat, lon)) where place is 
	English and lat and lon are float. Unfortunately, the structure of
	this list varies from geocoder to geocoder.
	"""
	results = gc.geocode(loc, region="us", exactly_one=False) # GoogleV3
#			results = gc.geocode(loc, exactly_one=False)
	if len(results)<1:
		raise LatLonException(loc+" returned no results")
	if len(results)==1:
		result = results[0]
	else:
		loc_median = median([(lat,lon) for place, (lat,lon) in results], axis=1)
		placenames = set([s.title() for s, (lat, lon) in results])
		result = ("median of {} points in {}".format(len(results), placenames), loc_median)
	if sanity_check and not sanity_checker(*result[1]):
		raise LatLonException(loc+" failed sanity check: "+str(result))
	return result
def lookup_lat_lon(loc, *args, **kwargs):
	global lat_lon_cache
	error_result = kwargs.pop('error_result', ("None", (None, None)))
	retry_on_errors = kwargs.pop('retry_on_errors', False)
	#
	key = loc.strip().upper()
	if key not in lat_lon_cache:
		try:
			lat_lon_cache[key] = fetch_lat_lon(loc, *args, **kwargs)
		except LatLonException:
			try:
				# try to get around a bug in GoogleV3 by doubling the placename
				loc2 = ' ; '.join((loc,)*2)
				lat_lon_cache[key] = fetch_lat_lon(loc2, *args, **kwargs)
			except Exception as e:
				error("Lookup of {} failed: {}".format(loc, e))
				if not retry_on_errors:
					lat_lon_cache[key] = error_result
				return error_result
	return lat_lon_cache[key]
if __name__ == '__main__':
	import sys
	for arg in sys.argv[1:]:
		place, (lat, lon) = lookup_lat_lon(arg)
		try:
			print place,"=","Lat:{:+03.5f}={},Lon:{:+03.5f}={}".format(lat, decdeg2dms(lat), lon, decdeg2dms(lon))
		except:
			print place, (lat, lon)
#	print lat_lon_cache

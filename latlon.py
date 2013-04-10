#! env python
"""
Resolve latitude/longitude from simple placenames. In the case of multiple
points returned from the web geocoder, the median is taken. It seems to work
best when ZIP is given.
If modifying the geocoder, note that geopy has slight implementation 
differences, see https://code.google.com/p/geopy/wiki/GettingStarted
"""
from geopy import geocoders
from numpy import median
import sys

lat_lon_cache = {}
#gc = geocoders.GeoNames(format_string="%s, USA")
gc = geocoders.GoogleV3()
def get_lat_lon(loc, *args, **kwargs):
	"""
	Coroutine for resolving a lat-lon pair from a city, with some caching to
	avoid being obnoxious. 
	"""
	key = loc.strip().upper()
	if key in lat_lon_cache:
		return lat_lon_cache[key]
	else:
		try:
			result = gc.geocode(loc, region="us", exactly_one=False) # GoogleV3
#			result = gc.geocode(loc, exactly_one=False)
			if isinstance(result, list):
				if len(result)<1:
					return ("None", (None, None))
				if len(result)==1:
					result = result[0]
				else:
					loc_median = median([(lat,lon) for place, (lat,lon) in result], axis=1)
					result = ("median of {} in {}".format(len(result), result[0][0]), loc_median)
			lat_lon_cache[key] = result
			return result
		except Exception as e:
			print >> sys.stderr, loc, "Failed:", e
if __name__ == '__main__':
	arg = ' '.join(sys.argv[1:])
	place, (lat, lon) = get_lat_lon(arg)
	print place,"=","Lat:{:+03.5f},Lon:{:+03.5f}".format(lat, lon)
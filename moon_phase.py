from datetime import datetime

import ephem
from pytz import timezone, utc

# to see a list of cities, use ephem.cities._city_data.keys()
try:
	here = ephem.city('Boulder')
except:
	here = ephem.Observer()
	here.name = 'Boulder'
	#here.lat, here.lon, here.elevation = 40, -105.17, 1700
	here.lat, here.lon, here.elevation = '40:1.28.30', '-105:15.35.09', 1700
tz = timezone('US/Mountain')

utcer = lambda d: utc.localize(d.datetime())
localtimer = lambda d: tz.normalize(d.astimezone(tz))

now = utc.localize(datetime.utcnow())
here.date = now

sun = ephem.Sun(here)
moon = ephem.Moon(here)
mars = ephem.Mars(here)

###
events = []
def append(*args):
	events.append(args)

# rising examples
append("Sunrise", here.next_rising(sun))
append("Moonrise", here.next_rising(moon))

# setting examples 
here.horizon='4' # add a custom value for Boulder
append("Sunset", here.next_setting(sun))
#append("Moonset", here.next_setting(moon))

# moon examples
append("Full moon", ephem.next_full_moon(here.date))

# solstice examples
append("Solstice", ephem.next_solstice(here.date))
append("Equinox", ephem.next_equinox(here.date))

#
events.sort(key = lambda et: et[-1])
for e, nt in events[:4]:
	t = utcer(nt)
	print e, localtimer(t), t-now
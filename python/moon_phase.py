from datetime import datetime

import ephem
from pytz import timezone, utc

def is_visible(body):
	alt = body.alt
	if (0 <= alt <= 180):
		return alt
	return None
# to see a list of cities, use ephem.cities._city_data.keys()
try:
	here = ephem.city('Boulder')
except:
	here = ephem.Observer()
	here.name = 'Boulder'
	#here.lat, here.lon, here.elevation = 40, -105.17, 1700
	here.lat, here.lon, here.elevation = '40:1.28.30', '-105:15.35.09', 1700
here.pressure = 0
tz = timezone('US/Mountain')

utcer = lambda d: utc.localize(d.datetime())
localtimer = lambda d: tz.normalize(d.astimezone(tz))

now = utc.localize(datetime.utcnow())
here.date = now

sun = ephem.Sun(here)
moon = ephem.Moon(here)
venus = ephem.Venus(here)
mars = ephem.Mars(here)
jupiter = ephem.Jupiter(here)
saturn = ephem.Saturn(here)

###
events = []
def append(*args):
	events.append(args)

# rising examples
append("Sunrise", here.next_rising(sun))
append("Moonrise", here.next_rising(moon))
append("Venus rise", here.next_rising(venus))
append("Mars rise", here.next_rising(mars))
append("Jupiter rise", here.next_rising(jupiter))
append("Saturn rise", here.next_rising(saturn))

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
if is_visible(moon):
	print "Moon",
if not is_visible(sun):
	print "Venus" if is_visible(venus) else "",
	print "Mars" if is_visible(mars) else "",
	print "Jupiter" if is_visible(jupiter) else "",
	print "Saturn" if is_visible(saturn) else "",
print "visible"

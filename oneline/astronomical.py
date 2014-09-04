from datetime import datetime, timedelta
from itertools import groupby
import math
import time

import ephem
import pytz

from local.xcollections import Namespace

utcnow = pytz.UTC.localize(datetime.utcnow())
 
degrees_per_radian = 180.0 / math.pi
 
home = ephem.Observer()
home.lat, home.lon = '40', '-104.5'	# +N, +E
home.elevation = 1700	# meters

def get_astronomy(observ=home, hours_after_sunset=3):
	t=ephem.localtime # time formatter
	observ.compute_pressure()
	n = Namespace()
	events = []
	if True:
		sun = ephem.Sun()
		sun.compute(observ)
		n['Sun'] = Namespace()
		n['Sun']['visible'] = (sun.alt > 0)
		events.append( (t(observ.next_rising(sun)), "sunrise") )
		events.append( (t(observ.next_setting(sun)), "sunset") )
	if True:
		moon = ephem.Moon()
		moon.compute(observ)
		n['moon'] = Namespace()
		n['moon']['visible'] = moon.moon_phase if (moon.alt > 0) else False
		_, n['moon']['constellation'] = ephem.constellation(moon)
		events.append( (t(observ.next_rising(moon)), "moon rises") )
		events.append( (t(observ.next_setting(moon)), "moon sets") )
		events.append( (t(ephem.next_full_moon(utcnow)), "full moon") )
		events.append( (t(ephem.next_new_moon(utcnow)), "new moon") )
	if hours_after_sunset:
		observ.date = observ.next_setting(sun)+ephem.hour*hours_after_sunset
	if True:
		for name, body in [ ('Mercury',		ephem.Mercury()),
							('Venus',		ephem.Venus()),
							('Mars',		ephem.Mars()),
							('Jupiter',		ephem.Jupiter()),
							('Saturn',		ephem.Saturn()),
							('Uranus',		ephem.Uranus()) ]:
			body.compute(observ)
			b = Namespace()
			if n.Sun.visible: # Note: different than moon
				v = b['visible'] = False
			else:
				v = b['visible'] = body.phase/100.0 if (body.alt > 0) else False
			_, b['constellation'] = ephem.constellation(body)
			events.append( (t(observ.next_rising(body)), name+" rises") )
			events.append( (t(observ.next_setting(body)), name+" sets") )
			n[name] = b
	events.sort()
	return events, n
#
def timedelta_to_string(td):
	if timedelta(days=-2) < td < timedelta(days=2):
		return "{:02.0f}h".format(td.total_seconds()/60/60)
	else:
		return "{:02d}d".format(td.days)
#
def print_events((events, bodies), now=None, relative=False):
	visibles = [ b for b, d in bodies.iteritems() if d.visible and b is not 'Sun' ]
	if visibles:
		lines = [ ", ".join(visibles)+" up" ]
	else:
		lines = []
	now = now or datetime.now()
	if relative:
		display_tuples = [ (timedelta_to_string(ts-now), e) for ts, e in events ]
	else:
		display_tuples = []
		for ts, e in events:
			if 'sun' in e.lower():
				display_tuples.append( (ts.strftime("%b %d"), ts.strftime("%X"), e) )
			else:
				display_tuples.append( (ts.strftime("%b %d"), ts.strftime("%Hh"), e) )
	for g, et in groupby(display_tuples, key=lambda t: t[0]):
		lines.append(g+": "+", ".join(h+" "+e for _, h, e in et))
	print " :".join(lines)[:160]
#
# TODO:
#
print_events(get_astronomy())
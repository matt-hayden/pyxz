from datetime import datetime
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
#home.date = datetime.utcnow()

def get_astronomy(observ=home, only_visible=False):
	observ.compute_pressure()

	n = Namespace()

	if True:
		sun = ephem.Sun()
		sun.compute(observ)
		n['sun'] = Namespace()
		n['sun']['visible'] = (sun.alt > 0)
		n['sun']['rise'] = ephem.localtime(observ.next_rising(sun))
		n['sun']['set'] = ephem.localtime(observ.next_setting(sun))

	if True:
		moon = ephem.Moon()
		moon.compute(observ)
		n['moon'] = Namespace()
		n['moon']['visible'] = moon.moon_phase if (moon.alt > 0) else 0
		_, n['moon']['constellation'] = ephem.constellation(moon)
		n['moon']['rise'] = ephem.localtime(observ.next_rising(moon))
		n['moon']['set'] = ephem.localtime(observ.next_setting(moon))

		n['moon']['full'] = ephem.localtime(ephem.next_full_moon(utcnow))
		n['moon']['new'] = ephem.localtime(ephem.next_new_moon(utcnow))

	if True:
		n['bodies'] = Namespace()
		for name, body in [ ('mercury',		ephem.Mercury()),
							('venus',		ephem.Venus()),
							('mars',		ephem.Mars()),
							('jupiter',		ephem.Jupiter()),
							('saturn',		ephem.Saturn()),
							('uranus',		ephem.Uranus()) ]:
			body.compute(observ)
			b = Namespace()
			v = b['visible'] = body.phase/100.0 if (body.alt > 0) else 0
			if only_visible and not v: continue
			_, b['constellation'] = ephem.constellation(body)
			b['rise'] = sort_order_raw = ephem.localtime(observ.next_rising(body))
			b['set'] = ephem.localtime(observ.next_setting(body))
			n.bodies[name] = b
	return n
#
n = get_astronomy()
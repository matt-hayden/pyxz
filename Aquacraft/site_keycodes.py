from keycodes import Keycode

# Waterloo was assigned up to 1304, but ballooned to 1319
ranges = { 'Denver':			Keycode('12S101', '12S226'),
		   'Fort Collins':		Keycode('12S230', '12S360'),
		   'Scottsdale':		Keycode('12S370', '12S489'),
		   'San Antonio':		Keycode('12S500', '12S609'),
		   'Clayton County':	Keycode('12S701', '12S810'),
		   'Toho':				Keycode('12S820', '12S917'),
		   'Peel':				Keycode('12S1001', '12S1122'),
		   'Waterloo':			Keycode('12S1201', '12S1319'),
		   'Tacoma':			Keycode('13S101', '13S215') }

def get_lookup_for_site_by_keycode():
	lookup = { k: s for s, r in ranges.items() for k in r }
	def caller(keycode, lookup=lookup):
		return lookup[Keycode(keycode)]
	return caller
from datetime import datetime, timedelta
from pytz import timezone

import pytz

fmt = '%a %d %H:%M %Z%z'

zones_by_location = [ ('Hamsterdam', 'US/Eastern'), ('Amsterdam', 'Europe/Amsterdam') ]

def tzshift(walltime=None, newzone='UTC'):
	if not walltime:
		walltime=pytz.UTC.localize(datetime.utcnow())
	newzone = timezone(newzone)
	return newzone.normalize(walltime)

def wallclock(zones_by_location=zones_by_location):
	for label, zone_name in zones_by_location:
		yield label, tzshift(newzone=zone_name).strftime(fmt)
print list(wallclock())
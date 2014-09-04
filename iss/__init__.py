import re

import dateutil.parser
import feedparser

from local.xcollections import Namespace

sighting_feed_url = '''http://spotthestation.nasa.gov/sightings/xml_files/United_States_Colorado_Boulder.xml'''

from track_feed import get_sightings

sightings = track_feed.get_sightings()
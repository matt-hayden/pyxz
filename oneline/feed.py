#!env python
#from datetime import datetime, timedelta
#import dateutil.parser
from xml.sax.saxutils import unescape

import feedparser
#import pytz # TODO

#now = datetime.now(tz=pytz.timezone('America/Denver'))
url = 'http://bouldercolorado.gov/index.php?option=com_content&view=category&layout=blog&id=858&Itemid=5747&format=feed&type=atom'
url = 'http://news.google.com/news?hl=en&gl=us&authuser=0&q=%22city+of+Boulder%22+colorado&um=1&ie=UTF-8&output=atom'
url = 'http://rss.wunderground.com/auto/rss_full/CO/Boulder.xml?units=metric'

feed = feedparser.parse(url)

"""
Not all feeds have an updated attribute:
#feed_updated = feed.updated_parsed # returns a time_struct
feed_updated = dateutil.parser.parse(feed.updated) # returns a datetime
#feed.entries.sort(key=lambda _: _.updated, reverse=True)
latest_entry = feed.entries[0]
latest_entry_age = now - dateutil.parser.parse(latest_entry.updated)

if latest_entry_age < timedelta(days=7):
	print latest_entry.title
"""

print unescape(feed.entries[0].summary)
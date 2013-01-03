#! python
### Extract the date from a url header, as an alternative to ntpdate
from datetime import datetime
import urllib2

url="https://www.google.com"
url="https://www.comcast.net"
date_string_format="%a, %d %b %Y %H:%M:%S %Z"
#
n, local_utcnow=datetime.now(), datetime.utcnow()
offset = n-local_utcnow
r=urllib2.urlopen(url)
d=datetime.strptime(r.headers['Date'], date_string_format)
diff = (local_utcnow-d).total_seconds()
if diff > 24*60:
	print "Local date is wrong, reset to", d
elif diff > 60:
	if (-300 < (diff % 60) < 300):
		print "Possibly a bad timezone:",
	print "Difference of %s seconds" % diff, "between server(%s) and local(%s) UTC" %(d,local_utcnow)
else:
	print d+offset
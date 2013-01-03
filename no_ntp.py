#! python
### Extract the date from a url header, as an alternative to ntpdate
from datetime import datetime
import re
import urllib2

url="https://www.google.com"
url="https://www.comcast.net"
date_liner=re.compile(r'\bDate:\s*(.+)\s*')
date_string_format="%a, %d %b %Y %H:%M:%S %Z"
take_any = True
#
n, local_utcnow=datetime.now(), datetime.utcnow()
offset = n-local_utcnow
r=urllib2.urlopen(url)
# print headers:
#print r.headers.headers
	
date_strings = []
for s in r.headers.headers:
	m = date_liner.match(s)
	if m:
		assert len(m.groups()) == 1
		if take_any:
			date_strings.append(m.groups()[0].strip() )
		else:
			date_strings = m.groups()[0].strip(),
			break
assert date_strings
# print all accepted dates:
#print date_strings
d=min([ datetime.strptime(s, date_string_format) for s in date_strings])
diff = (local_utcnow-d).total_seconds()
if diff > 24*60:
	print "Local date is wrong, reset to", d
elif diff > 60:
	if (-300 < (diff % 60) < 300):
		print "Possibly a bad timezone:",
	print "Difference of %s seconds" % diff, "between server(%s) and local(%s) UTC" %(d,local_utcnow)
else:
	print d+offset
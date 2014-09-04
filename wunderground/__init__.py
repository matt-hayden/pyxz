import re
import urllib2
import xml.etree.ElementTree as ET

import dateutil.parser

from local.xcollections import Namespace

key_string = '26ea4286e102b790'
conditions_url = 'http://api.wunderground.com/api/'+key_string+'/conditions/q/CO/Boulder.xml'
forecast_url = 'http://api.wunderground.com/api/'+key_string+'/forecast/q/CO/Boulder.xml'

from Forecast import _get_txtforecasts

forecasts = list(_get_txtforecasts())
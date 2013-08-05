import zipfile
def parse_zipinfo_date(zi, earliest=datetime(1980, 1, 1, 0, 0)):
	dt = datetime(*zi.date_time)
	return None if dt == earliest else dt
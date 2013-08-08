from logging import debug, info, warning, error, critical

try:
	import pandas as pd
	from as_panel import *
	MDB_File = pyodbc_MDB_pd
except ImportError:
	try:
		try:
			from local.xnp import *
		except:
			import numpy as np
		from as_array import *
		MDB_File = pyodbc_MDB_np
	except:
		from database_file import *

def is_sql(text, tokens=['SELECT ', 'INSERT ', 'CREATE ', 'DROP ', 'UPDATE '], strict=None):
	text = text.upper()
	for token in tokens:
		if text.startswith(token): return (text.endswith(';') if strict else True)
	else:
		raise ValueError("tokens argument must be a list of upper-case SQL tokens")
	return False
def sanitize_table_name(text):
	if text[0] != '[': text='['+text
	if text[-1] != ']': text=text+']'
	return text
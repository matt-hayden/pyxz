from logging import debug, info, warning, error, critical

try:
	import pandas as pd
	from as_panel import *
	MDB_File=pyodbc_MDB_pd
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

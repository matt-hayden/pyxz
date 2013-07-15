#!env python
from logging import debug, info, warning, error, critical

from collections import namedtuple
from contextlib import closing

from local.sanitize import sql_field_sanitize

def table_or_sql_statement(text, use_brackets=False):
	"""
	If the argument is not SQL, treat it like a table name and return
	select * from tablename;
	"""
	if isinstance(text, basestring):
		if any(_ in text.upper() for _ in ['SELECT ', 'INSERT ', 'CREATE ', 'DROP ', 'UPDATE ']):
			sql = text
		else:
			table_name = text
			if use_brackets:
				if not (table_name.startswith('[') and table_name.endswith(']')):
					table_name = '['+table_name+']'
			sql = 'select * from {};'.format(table_name)
		return sql
	return text

class _xdatabase_abstract(object):
	def __enter__(self):
		return self
	def __exit__(self, error_type, error_value, traceback):
		if not self.no_commit:
			self.commit()
	def commit(self, *args, **kwargs):
		self.connection.commit(*args, **kwargs)
	def cursor(self, *args, **kwargs):
		return closing(self.connection.cursor(*args, **kwargs))
	def execute(self, *args, **kwargs):
		cursor = self.connection.execute(*args, **kwargs)
		return closing(cursor)
	def executemany(self, *args, **kwargs):
		with self.cursor() as cursor:
			cursor.executemany(*args, **kwargs)
class _xdatabase_base(_xdatabase_abstract):
	def generate_table(self, *args, **kwargs):
		"""
		Optional keyword arguments:
			sql or SQL: syntax to execute
			cursor: cursor object to re-use
			parameters: a tuple that replaces '?' in SQL syntax
			named: returned iterable is a namedtuple based on field names (This
				is not supported by all drivers)
		"""
		sql = table_or_sql_statement(args[0])
		args = (sql,)+args[1:]
		with self.execute(*args, **kwargs) as cursor:
			try:
				Row=namedtuple('Row', self.get_field_names_for_cursor(cursor) )
				for _ in cursor:
					yield Row(*_)
			except:
				for _ in cursor:
					yield _
	def create_table(self,
					 table_name,
					 fields,
					 field_types = [],
					 **kwargs):
		if isinstance(fields, basestring):
			fields = fields.split()
		for fnumber, fname in enumerate(fields):
			sn = sql_field_sanitize(fname)
			if fname.upper() != sn.upper():
				warning("Field {} renamed to {}".format(fname, sn))
				fields[fnumber] = sn
		nfields = len(fields)
		
		if isinstance(field_types, basestring):
			field_types = field_types.split()
		if field_types:
			assert len(field_types) == nfields
		else:
			field_types = (self.default_field_type,)*nfields
		field_def = ', '.join(n+' '+t for n, t in zip(fields, field_types))
		create_sql = 'CREATE TABLE {0} ({1});'.format(table_name, field_def)
		debug("create_table(sql = '{}')".format(create_sql))
		with self.execute(create_sql):
			self.connection.commit()
	def get_create_coroutine(self,
							 table_name,
							 fields,
							 field_types = [],
							 **kwargs):
		ID_name = kwargs.pop('ID', '')
		if isinstance(fields, basestring):
			fields = fields.split()
		if isinstance(field_types, basestring):
			field_types = field_types.split()
		#
		create_fields = fields
		if ID_name:
			create_fields = [ID_name]+fields
			field_types.insert(0, self.default_ID_field_type)
		try:
			self.create_table(table_name, create_fields, field_types)
		except sqlite.OperationalError as e:
			if not 'already exists' in e.message:
				raise e
		return self.get_append_coroutine(table_name, fields, **kwargs)
	def get_append_coroutine(self,
							 table_name,
							 fields,
							 **kwargs):
		if isinstance(fields, basestring):
			fields = fields.split()
		nfields = len(fields)
		append_sql = 'INSERT INTO {0}({1}) VALUES ({2});'.format(table_name,
			', '.join(fields),
			','.join(('?',)*nfields))
		debug("get_append_coroutine(sql = '{}')".format(append_sql))
		def coroutine(sql):
			with self.cursor() as cursor:
				iteration = 0 # 1 will be added to this upon next() below, syncronizing it with sqlite AUTOINCREMENT
				try:
					while True:
						content = (yield iteration)
						if content:
							debug("Iteration {}: {}".format(iteration, content))
#							if len(content) != nfields:
#								print "Content has {} fields, expected {}".format(len(content), nfields)
#								print "Content: {}".format(content)
							cursor.execute(sql, content)
						else:
							info("Skipped iteration {}: no data".format(iteration))
						iteration += 1
				except GeneratorExit:
					debug("Iteration {} completed: {}".format(iteration-1, content))
#					cursor.commit()
		co = coroutine(sql=append_sql)
		co.next()
		return co
###
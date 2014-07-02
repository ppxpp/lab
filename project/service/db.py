#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb
import time
import itertools
import os

try:
	import MySQLdb.constants
	import MySQLdb.converters
	import MySQLdb.cursors
except ImportError:
	if 'READTHEDOCS' in os.environ:
		MySQLdb = None
	else:
		raise


class Row(dict):
	def __getattr__(self, name):
		try:
			return self[name]
		except KeyError:
			raise AttributeError(name)

class Connection(object):

	def __init__(self, host, port, database, user, password, max_idle_time = 7 * 3600):
		self.host = host
		self.port = port
		self.database = database
		self.max_idle_time = max_idle_time

		args = dict(use_unicode = True, charset = "utf8",
					db = database, init_command = 'set time_zone = "+8:00"', sql_mode = "TRADITIONAL")
		args['user'] = user
		args['passwd'] = password
		args['host'] = host
		args['port'] = port

		self._db = None
		self._db_args = args
		self._last_use_time = time.time()

		try:
			self.reconnect()
		except Exception:
			print "Cannot connect to database:%s of MySQL on %s:%s using user_name:%s password:%s" %(self.database, self.host, self.port, self._db_args['user'], self._db_args['passwd'])

	def __del__(self):
		self.close()

	def close(self):
		"""close MySQL connection"""
		if getattr(self, '_db', None) is not None:
			self._db.close()
			self._db = None

	def reconnect(self):
		"""close the existing database connection and re-opens it"""
		self.close()
		self._db = MySQLdb.connect(**self._db_args)
		self._db.autocommit(True)

	def iter(self, query, *parameters):
		"""returns an iterator for the given query and parameters"""
		self._ensure_connected()
		cursor = MySQLdb.cursors.SSCursor(self._db)
		try:
			self._execute(cursor, query, parameters)
			column_names = [d[0] for d in cursor.description]
			for row in cursor:
				yield Row(zip(column_names, row))
		finally:
			cursor.close()

	def query(self, query, parameters):
		"""Returns a row list for the given query and parameters"""
		cursor = self._cursor()
		try:
			self._execute(cursor, query, parameters)
			column_names = [d[0] for d in cursor.description]
			return [Row(itertools.izip(column_names, row)) for row in cursor]
		finally:
			cursor.close()

	def get(self, query, parameters = None):
		"""return the first row returned for the given query"""
		rows = self.query(query, parameters)
		if not rows:
			return None
		elif len(rows) > 1:
			raise Exception('Multiple rows returned for Database.get() query')
		else:
			return rows[0]

	def execute(self, query, parameters):
		"""execute the given query, returning the lastrowid from the query"""
		return self.execute_lastrowid(query, parameters)

	def execute_lastrowid(self, query, parameters):
		"""execute the given query, returning the rowcount from the query"""
		cursor = self._cursor()
		try:
			self._execute(cursor, query, parameters)
			return cursor.rowcount
		finally:
			cursor.close()

	def execute_rowcount(self, query, parameters):
		cursor = self._cursor()
		try:
			self._execute(cursor, query, parameters)
			return cursor.rowcount
		finally:
			cursor.close()

	def executemany(self, query, parameters):
		"""execute the given query against all the given param sequences. we return the lastrowid from the query"""
		print parameters
		return self.executemany_lastrowid(query, parameters)

	def executemany_lastrowid(self, query, parameters):
		"""executes the given query against all the given param sequences. we return the lastrowid from thr query"""
		cursor = self._cursor()
		try:
			cursor.executemany(query, parameters)
			return cursor.lastrowid
		finally:
			cursor.close()

	def executemany_rowcount(self, query, parameters):
		"""execute the given query against all the given param sequesces. we return the rowcount from query"""
		cursor = self._cursor()
		try:
			cursor.executemany(query, parameters)
			return cursor.rowcount
		finally:
			cursor.close()

	def _ensure_connected(self):
		if(self._db is None or (time.time() - self._last_use_time > self.max_idle_time)):
			self.reconnect()
			self._last_use_time = time.time()

	def _cursor(self):
		self._ensure_connected()
		return self._db.cursor()

	def _execute(self, cursor, query, parameters):
		try:
			return cursor.execute(query, parameters)
		except Exception:
			print "Error connecting to MySQL on %s" %(self.host)
			self.close()
			raise
	




if __name__ == '__main__':

	db = Connection('localhost', 3306, 'test','root', 'root')
	#print db.execute("update user set name = %s where id = %s", ["ooo", 4])

	#print db.execute('insert into user (name) values (%s)', ['nn'])

	print db.query('select * from user where id = %s', '30')
	#for row in db.query('select * from user where id = %s', '30'):
	#	print str(row.id) + ', ' + row.name
	"""
	print db.executemany('delete from user where id = %s', range(14, 30))
	for row in db.query('select * from user'):
		print str(row.id) + ', ' + row.name
	"""
	db.close()






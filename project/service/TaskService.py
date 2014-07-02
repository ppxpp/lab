#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/..")

import db

from utils import *


class TaskService(object):

	def __init__(self, config):
		
		if config is None:
			raise Exception
		self.conn = db.Connection(config.get('database', 'host'),
							 config.getint('database', 'port'),
							 config.get('database', 'db'),
							 config.get('database', 'user'),
							 config.get('database', 'passwd')
							 )


	def __del__(self):
		if getattr(self, 'conn', None) is not None:
			self.conn.close()

	"""
	根据task_uuid来获取记录
	fields 指定取出的列，并指定列的别名。如：fileds = ['task_uuid', 'task_name', {'id':'table_id', 'status':'task_status'}, 'delete']
	"""
	def getTaskByUUID(self, uuid, fields = None, includeDelete = False):
		"""根据uuid来查询对应的task记录"""
		selectField = '*'
		#----------此处代码存在SQL注入风险,字段的名字要确保正确
		if fields is not None and fields != '*':
			selectField = ''
			for item in fields:
				if type(item) == dict:
					for (k, v) in item.items():
						if selectField != '':
							selectField = selectField + ', '
						selectField = selectField + '`' + k + '`' + ' as `' + v + '` '
				elif type(item) == str:
					if selectField != '':
						selectField = selectField + ', '
					selectField = selectField + '`' + item + '` '
		#-----------
		sql = 'select ' + selectField + ' from `tbl_task` where `task_uuid` = %s'
		if includeDelete is False:
			sql = sql + ' and `delete` = 0'
		#注意sql注入
		#sql = 'select ' + selectField + ' from tbl_task where task_uuid = "' + uuid + '"'
		task = self.conn.get(sql, uuid)
		#task = self.conn.get(sql)
		return task


	"""
	添加task,并返回其id值
	"""
	def addNewTask(self, task):

		sql = 'insert into `tbl_task` ('
		sql_column = ''
		sql_values = ''
		sql_column_para = []
		for (k, v) in task.items():
			if sql_column != '':
				sql_column = sql_column + ', '
			sql_column = sql_column + '`' + k +'`'
			if sql_values != '':
				sql_values = sql_values + ', '
			sql_values = sql_values + '%s'
			sql_column_para.append(v)
		sql = sql + sql_column + ') values (' + sql_values + ')'
		self.conn.execute(sql, sql_column_para)
		#获取刚插入的记录的id号
		return self.getTaskByUUID(task['task_uuid'], {'id':'id'})['id']

	"""
	更新task
	"""
	def updateTask(self, task):
		sql = 'update tbl_task set '
		sql_set = ''
		sql_set_para = []
		for (k, v) in task.items():
			if k != 'task_uuid' and k != 'id':
				if sql_set != '':
					sql_set = sql_set + ', '
				sql_set = sql_set + '`' + k + '` = %s '
				sql_set_para.append(v)
		sql = sql + sql_set + ' where `task_uuid` = %s'
		sql_set_para.append(task['task_uuid'])
		return self.conn.execute(sql, sql_set_para)

	"""
	删除task，目前仅仅将delete字段赋值成非零值，并不从数据库中删除
	"""
	def deleteTask(self, task):
		_task = {}
		_task['task_uuid'] = task['task_uuid']
		_task['delete'] = int(time.time())
		return self.updateTask(_task)


if __name__ == "__main__":

	#db = Connection('localhost', 3306, 'test','root', 'root')
	config = config.getConfig()
	mTaskService = TaskService(config)
	#field = {'task_uuid':'uuid','task_name':'name', 'id':'tabe_id', 'owner':'user_name'}
	field = ['task_uuid', 'task_name', {'owner':'user_name', 'status':'sss'}, 'delete', {'id':'table_id'}]
	#print mTaskService.getTaskByUUID('111', field, False)
	#task = {'uuid':'908', 'owner':'john', 'status':'status_start', 'extra':'this is extra'}
	task = {'task_uuid':'69', 'task_name':'name', 'owner':'john', 'status':'status_start', 'extra':'{ "name": "cxh", "sex": "man" }'}
	print mTaskService.addNewTask(task)
	#print mTaskService.updateTask(task)
	#print mTaskService.deleteTask(task)
	#print task


















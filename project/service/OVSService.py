#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/..")

import db

from utils import *


class OVSService(object):

	def __init__(self, config):
		
		if config is None:
			raise Exception
		self.columns = ['id', 'ovs_uuid', 'task_uuid', 'ovs_name', 'delete']
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
	根据ovs_uuid来获取记录
	fields 指定取出的列，并指定列的别名。如：fileds = ['task_uuid', 'task_name', {'id':'table_id', 'status':'task_status'}, 'delete']
	"""
	def getOVSByUUID(self, uuid, fields = None, includeDelete = False):
		"""根据uuid来查询对应的vm记录"""
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
		#--------------------------------------------------------
		sql = 'select ' + selectField + ' from `tbl_ovs` where `ovs_uuid` = %s'
		if includeDelete is False:
			sql = sql + ' and `delete` = 0'
		#注意sql注入
		#sql = 'select ' + selectField + ' from tbl_task where task_uuid = "' + uuid + '"'
		task = self.conn.get(sql, uuid)
		#task = self.conn.get(sql)
		return task


	"""
	添加ovs,并返回其id值
	"""
	def addNewOVS(self, ovs):
		sql = 'insert into `tbl_ovs` ('
		sql_column = ''
		sql_values = ''
		sql_column_para = []
		#-------------------以下代码有SQL注入的风险，注意确保字段名正确
		for (k, v) in ovs.items():
			if not k in self.columns:
				continue
			if sql_column != '':
				sql_column = sql_column + ', '
			sql_column = sql_column + '`' + k +'`'
			if sql_values != '':
				sql_values = sql_values + ', '
			sql_values = sql_values + '%s'
			sql_column_para.append(v)
		sql = sql + sql_column + ') values (' + sql_values + ')'
		#-------------------------------------------------------------
		self.conn.execute(sql, sql_column_para)
		#获取刚插入的记录的id号
		return self.getOVSByUUID(ovs['ovs_uuid'], {'id':'id'})['id']

	"""
	更新ovs
	"""
	def updateOVS(self, ovs):
		sql = 'update tbl_ovs set '
		sql_set = ''
		sql_set_para = []
		#-------------------以下代码有SQL注入的风险，注意确保字段名正确
		for (k, v) in ovs.items():
			if k != 'ovs_uuid' and k != 'id':
				if not k in self.columns:
					continue
				if sql_set != '':
					sql_set = sql_set + ', '
				sql_set = sql_set + '`' + k + '` = %s '
				sql_set_para.append(v)
		sql = sql + sql_set + ' where `ovs_uuid` = %s'
		sql_set_para.append(ovs['ovs_uuid'])
		#-------------------------------------------------------------
		return self.conn.execute(sql, sql_set_para)

	"""
	删除ovs，目前仅仅将delete字段赋值成非零值，并不从数据库中删除
	"""
	def deleteOVS(self, ovs):
		_ovs = {}
		_ovs['ovs_uuid'] = ovs['ovs_uuid']
		_ovs['delete'] = int(time.time())
		return self.updateOVS(_ovs)


if __name__ == "__main__":

	#db = Connection('localhost', 3306, 'test','root', 'root')
	config = config.getConfig()
	mOVSService = OVSService(config)
	#field = ['ovs_uuid', 'ovs_name', {'ovs_status':'status'}, 'delete', {'id':'table_id'}]
	#print mOVSService.getOVSByUUID('61', field, False)
	#task = {'uuid':'908', 'owner':'john', 'status':'status_start', 'extra':'this is extra'}
	ovs = {'ovs_uuid':'61', 'task_uuid':'69', 'ovs_name':'this is new name','ovs_status':'status_start', 'ovs_extra':'{ "name": "cxh", "sex": "man" }'}
	#print mOVSService.addNewOVS(ovs)
	print mOVSService.updateOVS(ovs)
	#print mOVSService.deleteOVS(ovs)
	#print vm


















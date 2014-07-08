#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/..")

import db

from utils import *


class OVSPartService(object):

	def __init__(self, config):
		
		if config is None:
			raise Exception
		self.columns = ['id', 'ovs_part_uuid', 'ovs_uuid', 'ovs_part_mac', 'ovs_part_status', 'delete', 'host_uuid']
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
	根据ovs_part_uuid来获取记录
	fields 指定取出的列，并指定列的别名。如：fileds = ['task_uuid', 'task_name', {'id':'table_id', 'status':'task_status'}, 'delete']
	"""
	def getOVSPartByUUID(self, uuid, fields = None, includeDelete = False):
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
		sql = 'select ' + selectField + ' from `tbl_ovs_part` where `ovs_part_uuid` = %s'
		if includeDelete is False:
			sql = sql + ' and `delete` = 0'
		#注意sql注入
		#sql = 'select ' + selectField + ' from tbl_task where task_uuid = "' + uuid + '"'
		task = self.conn.get(sql, uuid)
		#task = self.conn.get(sql)
		return task


	"""
	添加ovs_part,并返回其id值
	"""
	def addNewOVSPart(self, ovspart):
		sql = 'insert into `tbl_ovs_part` ('
		sql_column = ''
		sql_values = ''
		sql_column_para = []
		#-------------------以下代码有SQL注入的风险，注意确保字段名正确
		for (k, v) in ovspart.items():
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
		return self.getOVSPartByUUID(ovspart['ovs_part_uuid'], {'id':'id'})['id']

	"""
	更新ovspart
	"""
	def updateOVSPart(self, ovspart):
		sql = 'update tbl_ovs_part set '
		sql_set = ''
		sql_set_para = []
		#-------------------以下代码有SQL注入的风险，注意确保字段名正确
		for (k, v) in ovspart.items():
			if k != 'ovs_part_uuid' and k != 'id':
				if not k in self.columns:
					continue
				if sql_set != '':
					sql_set = sql_set + ', '
				sql_set = sql_set + '`' + k + '` = %s '
				sql_set_para.append(v)
		sql = sql + sql_set + ' where `ovs_part_uuid` = %s'
		sql_set_para.append(ovspart['ovs_part_uuid'])
		#-------------------------------------------------------------
		return self.conn.execute(sql, sql_set_para)

	"""
	删除ovs，目前仅仅将delete字段赋值成非零值，并不从数据库中删除
	"""
	def deleteOVSPart(self, ovspart):
		_ovspart = {}
		_ovspart['ovs_part_uuid'] = ovspart['ovs_part_uuid']
		_ovspart['delete'] = int(time.time())
		return self.updateOVSPart(_ovspart)


if __name__ == "__main__":

	#db = Connection('localhost', 3306, 'test','root', 'root')
	config = config.getConfig()
	mOVSPartService = OVSPartService(config)
	field = ['ovs_part_uuid', 'ovs_uuid', {'ovs_part_status':'status'}, 'delete', {'id':'table_id'}]
	print mOVSPartService.getOVSPartByUUID('69', field, False)
	#task = {'uuid':'908', 'owner':'john', 'status':'status_start', 'extra':'this is extra'}
	obj = {'ovs_uuid':'xxxx', 'ovs_part_uuid':'69', 'ovs_part_mac':'ff:dd:aa:22:23:a2','ovs_part_status':'status_start', 'host_uuid':'host_uuid_uuid'}
	#print mOVSPartService.addNewOVSPart(obj)
	print mOVSPartService.updateOVSPart(obj)
	#print mOVSPartService.deleteOVSPart(obj)
	#print vm


















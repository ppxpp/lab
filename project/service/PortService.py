#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/..")

import db

from utils import *


class PortService(object):

	def __init__(self, config):
		
		if config is None:
			raise Exception
		self.columns = ['id', 'port_uuid', 'port_type', 'vlan_tag', 'device_uuid', 'port_protocol', 'port_mac', 'delete']
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
	根据port_uuid来获取记录
	fields 指定取出的列，并指定列的别名。如：fileds = ['task_uuid', 'task_name', {'id':'table_id', 'status':'task_status'}, 'delete']
	"""
	def getPortByUUID(self, uuid, fields = None, includeDelete = False):
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
		sql = 'select ' + selectField + ' from `tbl_port` where `port_uuid` = %s'
		if includeDelete is False:
			sql = sql + ' and `delete` = 0'
		#注意sql注入
		#sql = 'select ' + selectField + ' from tbl_task where task_uuid = "' + uuid + '"'
		task = self.conn.get(sql, uuid)
		#task = self.conn.get(sql)
		return task


	"""
	添加port,并返回其id值
	"""
	def addNewPort(self, port):

		sql = 'insert into `tbl_port` ('
		sql_column = ''
		sql_values = ''
		sql_column_para = []
		#-------------------以下代码有SQL注入的风险，注意确保字段名正确
		for (k, v) in port.items():
			if k in self.columns:
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
		return self.getPortByUUID(port['port_uuid'], {'id':'id'})['id']

	"""
	更新port
	"""
	def updatePort(self, port):
		sql = 'update tbl_port set '
		sql_set = ''
		sql_set_para = []
		for (k, v) in port.items():
			if k != 'port_uuid' and k != 'id':
				if sql_set != '':
					sql_set = sql_set + ', '
				sql_set = sql_set + '`' + k + '` = %s '
				sql_set_para.append(v)
		sql = sql + sql_set + ' where `port_uuid` = %s'
		sql_set_para.append(port['port_uuid'])
		return self.conn.execute(sql, sql_set_para)

	"""
	删除port，目前仅仅将delete字段赋值成非零值，并不从数据库中删除
	"""
	def deletePort(self, port):
		_port = {}
		_port['port_uuid'] = port['port_uuid']
		_port['delete'] = int(time.time())
		return self.updatePort(_port)


if __name__ == "__main__":

	#db = Connection('localhost', 3306, 'test','root', 'root')
	config = config.getConfig()
	mPortService = PortService(config)
	#field = {'task_uuid':'uuid','task_name':'name', 'id':'tabe_id', 'owner':'user_name'}
	field = ['port_uuid', 'port_type', {'vlan_tag':'vlan', 'device_uuid':'device'}, 'delete', {'id':'table_id'}]
	print mPortService.getPortByUUID('69', field, False)
	#print mPortService.getPortByUUID('69', field, True)
	#port = {'uuid':'908', 'owner':'john', 'status':'status_start', 'extra':'this is extra'}
	port = {'port_uuid':'69', 'port_type':'type_ovs', 'device_uuid':'12131313131', 'port_mac':'a1:34:ef:77:f0:87'}
	#print mPortService.addNewPort(port)
	#print mPortService.updatePort(port)
	print mPortService.deletePort(port)
	#print task


















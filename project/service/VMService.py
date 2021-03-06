#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/..")

import db

from utils import *


class VMService(object):

	def __init__(self, config):
		
		if config is None:
			raise Exception
		self.columns = ['id', 'vm_uuid', 'task_uuid', 'host_uuid', 'vm_name', 'vm_image', 'vm_flavor', 'vm_status', 'delete']
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
	根据vm_uuid来获取记录
	fields 指定取出的列，并指定列的别名。如：fileds = ['task_uuid', 'task_name', {'id':'table_id', 'status':'task_status'}, 'delete']
	"""
	def getVMByUUID(self, uuid, fields = None, includeDelete = False):
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
		sql = 'select ' + selectField + ' from `tbl_vm` where `vm_uuid` = %s'
		if includeDelete is False:
			sql = sql + ' and `delete` = 0'
		#注意sql注入
		#sql = 'select ' + selectField + ' from tbl_task where task_uuid = "' + uuid + '"'
		task = self.conn.get(sql, uuid)
		#task = self.conn.get(sql)
		return task


	"""
	添加vm,并返回其id值
	"""
	def addNewVM(self, vm):
		sql = 'insert into `tbl_vm` ('
		sql_column = ''
		sql_values = ''
		sql_column_para = []
		#-------------------以下代码有SQL注入的风险，注意确保字段名正确
		for (k, v) in vm.items():
			
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
		return self.getVMByUUID(vm['vm_uuid'], {'id':'id'})['id']

	"""
	更新vm
	"""
	def updateVM(self, vm):
		sql = 'update tbl_vm set '
		sql_set = ''
		sql_set_para = []
		#-------------------以下代码有SQL注入的风险，注意确保字段名正确
		for (k, v) in vm.items():
			if k != 'vm_uuid' and k != 'id':
				if sql_set != '':
					sql_set = sql_set + ', '
				sql_set = sql_set + '`' + k + '` = %s '
				sql_set_para.append(v)
		sql = sql + sql_set + ' where `vm_uuid` = %s'
		sql_set_para.append(vm['vm_uuid'])
		#-------------------------------------------------------------
		return self.conn.execute(sql, sql_set_para)

	"""
	删除vm，目前仅仅将delete字段赋值成非零值，并不从数据库中删除
	"""
	def deleteVM(self, vm):
		_vm = {}
		_vm['vm_uuid'] = vm['vm_uuid']
		_vm['delete'] = int(time.time())
		return self.updateVM(_vm)


if __name__ == "__main__":

	#db = Connection('localhost', 3306, 'test','root', 'root')
	config = config.getConfig()
	mVMService = VMService(config)
	#field = {'task_uuid':'uuid','task_name':'name', 'id':'tabe_id', 'owner':'user_name'}
	#field = ['vm_uuid', 'vm_name', {'vm_image':'image', 'vm_status':'status', 'vm_flavor':'flavor'}, 'delete', {'id':'table_id'}]
	#print mVMService.getVMByUUID('619', field, False)
	#task = {'uuid':'908', 'owner':'john', 'status':'status_start', 'extra':'this is extra'}
	vm = {'vm_uuid':'619', 'task_uuid':'69', 'vm_name':'new name', 'vm_image':'john', 'vm_flavor':'this is flavor id', 'vm_status':'status_start', 'vm_extra':'{ "name": "cxh", "sex": "man" }'}
	print mVMService.addNewVM(vm)
	#print mVMService.updateVM(vm)
	#print mVMService.deleteVM(vm)
	#print vm


















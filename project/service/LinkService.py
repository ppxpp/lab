#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/..")

import db

from utils import *


class LinkService(object):

	def __init__(self, config):
		
		if config is None:
			raise Exception
		self.columns = ['id', 'link_uuid', 'task_uuid', 'link_status', 'delete', 'link_port1_uuid', 'link_port2_uuid']
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
	根据link_uuid来获取记录
	fields 指定取出的列，并指定列的别名。如：fileds = ['task_uuid', 'task_name', {'id':'table_id', 'status':'task_status'}, 'delete']
	"""
	def getLinkByUUID(self, uuid, fields = None, includeDelete = False):
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
		sql = 'select ' + selectField + ' from `tbl_link` where `link_uuid` = %s'
		if includeDelete is False:
			sql = sql + ' and `delete` = 0'
		#注意sql注入
		#sql = 'select ' + selectField + ' from tbl_task where task_uuid = "' + uuid + '"'
		task = self.conn.get(sql, uuid)
		#task = self.conn.get(sql)
		return task


	"""
	添加link,并返回其id值
	"""
	def addNewLink(self, link):

		sql = 'insert into `tbl_link` ('
		sql_column = ''
		sql_values = ''
		sql_column_para = []
		#-------------------以下代码有SQL注入的风险，注意确保字段名正确
		for (k, v) in link.items():
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
		return self.getLinkByUUID(link['link_uuid'], {'id':'id'})['id']

	"""
	更新link
	"""
	def updateLink(self, link):
		sql = 'update tbl_link set '
		sql_set = ''
		sql_set_para = []
		for (k, v) in link.items():
			if k != 'link_uuid' and k != 'id':
				if sql_set != '':
					sql_set = sql_set + ', '
				sql_set = sql_set + '`' + k + '` = %s '
				sql_set_para.append(v)
		sql = sql + sql_set + ' where `link_uuid` = %s'
		sql_set_para.append(link['link_uuid'])
		return self.conn.execute(sql, sql_set_para)

	"""
	删除link，目前仅仅将delete字段赋值成非零值，并不从数据库中删除
	"""
	def deleteLink(self, link):
		_link = {}
		_link['link_uuid'] = link['link_uuid']
		_link['delete'] = int(time.time())
		return self.updateLink(_link)


if __name__ == "__main__":

	#db = Connection('localhost', 3306, 'test','root', 'root')
	config = config.getConfig()
	mLinkService = LinkService(config)
	#field = {'task_uuid':'uuid','task_name':'name', 'id':'tabe_id', 'owner':'user_name'}
	field = ['link_uuid', 'task_uuid', {'link_status':'status', 'link_port1_uuid':'port1_uuid'}, 'delete', {'link_port2_uuid':'port2_uuid'}]
	print mLinkService.getLinkByUUID('69', field, False)
	print mLinkService.getLinkByUUID('69', field, True)
	#port = {'uuid':'908', 'owner':'john', 'status':'status_start', 'extra':'this is extra'}
	link = {'link_uuid':'69', 'task_uuid':'task_9999', 'link_status':'link_statue_wait', 'link_port1_uuid':'11111', 'link_port2_uuid':'2222'}
	#print mLinkService.addNewLink(link)
	#print mLinkService.updateLink(link)
	print mLinkService.deleteLink(link)
	#print task


















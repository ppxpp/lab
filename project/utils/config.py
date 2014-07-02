#!/usr/bin/python
#-*- coding: utf-8 -*-

import os
import ConfigParser


def getConfig(configFile = os.path.dirname(os.path.realpath(__file__)) + '/../conf/config.ini'):
	"""从configFile读取配置信息，默认使用config.ini文件"""
	config = ConfigParser.RawConfigParser()
	config.read(configFile)
	return config


if __name__ == '__main__':
	config = getConfig()
	print config.get('default', 'name')
	print config.get('database', 'host')
	print config.getint('database', 'port')

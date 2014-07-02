#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import logging
import logging.config

import config
logfile = config.getConfig().get('default', 'logfile')
if os.path.exists(logfile) is False:
	os.mknod(logfile)
logging.basicConfig(filename=logfile,
					filemode = 'w',
					level=logging.DEBUG, 
					format='%(asctime)s - %(name)s - %(levelname)s : %(message)s')


def e(msg):
	print msg
	#logging.error(msg)

def d(msg):
	print msg
	#logging.debug(msg)

def w(msg):
	print msg
	#logging.warn(msg)

def i(msg):
	print msg
	#logging.info(msg)

if __name__ == '__main__':
	d('this is debug')
	w('this is warn')
	i('this is info')

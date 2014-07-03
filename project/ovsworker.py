#/usr/bin/python
#-*- coding: utf-8 -*-

import sys, getopt
import os
import time
import random
import json



from utils import config as CONFIG
from utils import log as Log
from service import TaskService as TaskService
from service import VMService as VMService
from service import OVSService as OVSService

cfg = CONFIG.getConfig()


"""
创建ovs
输入参数：
ovs_part的uuid

填入数据库的字段包括：
1.ovs_part的mac地址
"""
def createOVSPart(gearman_worker, gearman_job):

	return ''



if __name__ == '__main__':
	createOVS()

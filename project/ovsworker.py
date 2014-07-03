#/usr/bin/python
#-*- coding: utf-8 -*-

import sys, getopt
import os
import time
import random
import json
import commands


from utils import config as CONFIG
from utils import log as Log
from service import TaskService as TaskService
from service import VMService as VMService
from service import OVSPartService as OVSPartService

cfg = CONFIG.getConfig()


"""
创建ovs
输入参数：
ovs_part的uuid

填入数据库的字段包括：
1.ovs_part的mac地址
"""
def createOVSPart(gearman_worker, gearman_job):
	ovspart_uuid = '69'
	mOVSPartService = OVSPartService.OVSPartService(cfg)

	ovsPart = mOVSPartService.getOVSPartByUUID(ovspart_uuid)

	out = commands.getstatusoutput('ovs-vsctl add-br ovs-' + ovspart_uuid)
	if int(out[0]) != 0:
		Log.e('create ovs error. ' + out[1])
		ovs_part = {'ovs_part_uuid':ovspart_uuid, 'ovs_part_status':'ovs_part_status_error'}
		mOVSPartService.updateOVSPart(ovs_part)
		return ''
	#获取mac地址
	out = commands.getstatusoutput('ifconfig | grep ovs-' + ovspart_uuid + ' | awk \'{print $5}\'')
	if int(out[0]) != 0 or out[1] == '':
		Log.e('cannot get mac address. ' + out[1])

	mac = out[1];
	ovs_part = {'ovs_part_uuid':ovspart_uuid, 'ovs_part_mac':mac, 'ovs_part_status':'ovs_part_status_success'}
	mOVSPartService.updateOVSPart(ovs_part)
	return ''



if __name__ == '__main__':
	createOVSPart(None, None)

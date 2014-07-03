#/usr/bin/python
# -*- coding: utf-8 -*-

import sys, getopt
import xml.etree.ElementTree as ET
import logging
import logging.config
import os
import time
import random
import gearman

from utils import config as CONFIG
from utils import log as Log
from service import TaskService as TaskService
from service import VMService as VMService
from service import OVSService as OVSService

"""
logging.basicConfig(filename='log/project.log',
					filemode = 'w',
					level=logging.DEBUG, 
					format='%(asctime)s - %(name)s - %(levelname)s : %(message)s')
logging.info('info logging')
logging.warn('warn logging')
"""
#print os.path.abspath(os.path.dirname(__file__))
#logging.config.fileConfig(os.path.abspath(os.path.dirname(__file__)) + "/logger.conf")

#从xml文件提取虚拟机信息
def getVMList(xmlPath):
	vmList = []
	tree = ET.parse(xmlPath)
	root = tree.getroot()
	for vmNode in root.find('vms').findall('vm'):
		vm = {}
		vm['vm_name'] = vmNode.get('name')
		vm['vm_uuid'] = str(int(time.time())) + str(random.randrange(100,1000))
		vm['vm_image'] = vmNode.find('image').text
		vm['vm_flavor'] = vmNode.find('flavor').text
		vmList.append(vm)
		#print vm
	return vmList

#从xml文件提取OVS交换机信息
def getOVSList(xmlPath):
	ovsList = []
	tree = ET.parse(xmlPath)
	root = tree.getroot()
	for ovsNode in root.find('switches').findall('ovs'):
		ovs = {}
		ovs['ovs_name'] = ovsNode.get('name')
		ovs['ovs_uuid'] = str(int(time.time())) + str(random.randrange(100,1000))
		ovsList.append(ovs)
	return ovsList


#提取拓扑信息
def getTopology(xmlPath):
	tree = ET.parse(xmlPath)
	root = tree.getroot()
	#默认的vlan tag
	defaultVlanTag = root.find('topology').find('default_vlan_tag').text
	#获取连接信息
	linkList = []
	for linkNode in root.find('topology').findall('link'):
		link  = []
		for endpointNode in linkNode.findall('endpoint'):
			endpoint = {}
			endpoint['type'] = endpointNode.find('type').text
			endpoint['name'] = endpointNode.find('name').text
			interface = endpointNode.find('interface')
			if type(interface) != type(None):
				endpoint['interface'] = interface.text
			vlanTag = endpointNode.find('vlan_tag')
			if type(vlanTag) != type(None):
				endpoint['vlan_tag'] = vlanTag.text
			else:
				endpoint['vlan_tag'] = defaultVlanTag
			link.append(endpoint)
		linkList.append(link)
	return linkList



def main():
	#taskXMLPath = ''
	opts, args = getopt.getopt(sys.argv[1:], "hi:", ["help", "input="])	
	for op, value in opts:
		if op == '--input' or op == '-i':
			#xml文件路径
			taskXMLPath = value
	#print taskXMLPath
	taskXMLPath = '/Users/zhouhao/baiduyun/lab/code/task.xml'
	#虚拟机列表
	vmList = getVMList(taskXMLPath)
	print vmList
	
	

	task = {}
	#在数据库创建任务记录
	taskUUID = str(int((time.time())))  + str(random.randrange(100, 1000))
	#print taskUUID
	task['task_uuid'] = taskUUID
	task['task_name'] = 'name'
	task['owner'] = 'default'
	task['status'] = 'status_start'
	
	config = CONFIG.getConfig()
	mTaskService = TaskService.TaskService(config)
	#task['id'] =  mTaskService.addNewTask(task)

	#将虚拟机信息填入数据表
	mVMService = VMService.VMService(config)
	for vm in vmList:
		vm['vm_status'] = 'vm_status_wait'
		vm['task_uuid'] = task['task_uuid']
		#vm['id'] = mVMService.addNewVM(vm)
	
	#gmClient = gearman.GearmanClient([config.get('gearman', 'server')])
	jobs = []
	for vm in vmList:
		job = {}
		job['task'] = 'createVirtualMachine'
		job['data'] = vm['vm_uuid']
		jobs.append(job)
	print jobs
	#submitted_requests = gmClient.submit_multiple_jobs(jobs, background = True, wait_until_complete = False)
	#print submitted_requests

	#gmClient = gearman.GearmanClient(['172.16.0.2:4330'])
	#jobRequest = gmClient.submit_job('job name', 'arbitary binary data', priority = gearman.PRIORITY_HIGH, background = True, wait_until_complete = False)
	#print jobRequest
	#list_of_jobs = [dict(task="task_name", data="binary data"), dict(task="other_task", data="other binary data")]
	#submitted_requests = gmClient.submit_multiple_jobs(list_of_jobs, background=False, wait_until_complete=False)
	#print submitted_requests


	#ovs交换机列表
	ovsList = getOVSList(taskXMLPath)
	print ovsList
	#将ovs信息填入数据表
	mOVSService = OVSService.OVSService(config)
	for ovs in ovsList:
		ovs['ovs_status'] = 'ovs_status_wait'
		ovs['task_uuid'] = task['task_uuid']
		#ovs['id'] = mOVSService.addNewOVS(ovs)
		Log.d(ovs)
	
	#link信息
	topology = getTopology(taskXMLPath)
	print topology	





















#execute main function
if __name__ == '__main__':
	main()
	#project.help()

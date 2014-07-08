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
import json

from utils import config as CONFIG
from utils import log as Log
from service import TaskService as TaskService
from service import VMService as VMService
from service import OVSService as OVSService
from service import PortService as PortService

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

def addInterfaceForVM(vm):
	#为vm添加一个网卡接口
	port = {}
	port['port_uuid'] = str(int(time.time())) + str(random.randrange(100, 1000))
	port['port_type'] = 'type_vm'
	port['device_uuid'] = vm['vm_uuid']
	#该属性在确立link时使用
	port['used'] = False
	if vm.get('vm_ports') is None:
		vm['vm_ports'] = []
	vm['vm_ports'].append(port)


#获取虚拟机的一个未使用的接口
def getFirstUnusedInterfaceForVM(vm):
	if vm.get('vm_ports') is None:
		return None
	ports = vm['vm_ports']
	for port in ports:
		if port['used'] == False:
			return port
	return None



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

	task = {}
	#在数据库创建任务记录
	taskUUID = str(int((time.time())))  + str(random.randrange(100, 1000))
	#print taskUUID
	task['task_uuid'] = taskUUID
	task['task_name'] = 'name'
	task['task_owner'] = 'default'
	task['task_status'] = 'status_start'
	
	config = CONFIG.getConfig()
	mTaskService = TaskService.TaskService(config)
	#task['id'] =  mTaskService.addNewTask(task)

	
	
	#link信息
	topologys = getTopology(taskXMLPath)

	#从拓扑结构推测出vm的接口信息
	for vm in vmList:
		for link in topologys:
			if link[0]['type'] == 'vm' and link[0]['name'] == vm['vm_name']:
				#增加一个接口
				addInterfaceForVM(vm)
			elif link[1]['type'] == 'vm' and link[1]['name'] == vm['vm_name']:
				#增加一个接口
				addInterfaceForVM(vm)
	
	#将虚拟机信息，port信息写入数据库
	mVMService = VMService.VMService(config)
	mPortService = PortService.PortService(config)
	for vm in vmList:
		vm['vm_status'] = 'vm_status_wait'
		vm['task_uuid'] = task['task_uuid']
		#将vm的port信息写入数据库
		if not vm.get('vm_ports') is None:
			for port in vm['vm_ports']:
				a;
				#mPortService.addNewPort(port)
		#将vm写入数据库
		#vm['id'] = mVMService.addNewVM(vm)
	#提交虚拟机创建任务，并等待任务执行结束
	#gmClient = gearman.GearmanClient([config.get('gearman', 'server')])
	#jobs = []
	#for vm in vmList:
	#	job = {}
	#	job['task'] = 'createVirtualMachine'
	#	job['data'] = vm['vm_uuid']
	#	jobs.append(job)
	#print jobs
	#submitted_requests = gmClient.submit_multiple_jobs(jobs, background = True, wait_until_complete = False)
	#print submitted_requests

	#gmClient = gearman.GearmanClient(['172.16.0.2:4330'])
	#jobRequest = gmClient.submit_job('job name', 'arbitary binary data', priority = gearman.PRIORITY_HIGH, background = True, wait_until_complete = False)
	#print jobRequest
	#list_of_jobs = [dict(task="task_name", data="binary data"), dict(task="other_task", data="other binary data")]
	#submitted_requests = gmClient.submit_multiple_jobs(list_of_jobs, background=False, wait_until_complete=False)
	#print submitted_requests


	#模拟worker在后台进行虚拟机创建，仅用于代码测试
	for vm in vmList:
		vm['host_uuid'] = 'host_uuid_uuid_' + str(random.randrange(10, 99))
		#print vm


	#ovs交换机列表
	ovsList = getOVSList(taskXMLPath)

	#print '\nlinks:\n'
	#for link in topologys:
	#	print link


	#计算实际需要的link
	necessaryLinks = []

	# 确定ovs有几个ovs_part
	# 1. 若ovs直接只通过trunk口连接，则只取决于该ovs与vm的连接关系
	#    因为每个计算节点都有一个出口ovs，该计算节点上的所有其他ovs都会与出口ovs相连，
	#    所以分布在不同计算节点上的ovs实际上已经是相连的
	# 2. 若ovs直接也通过access口连接，则取决于该ovs与vm以及其他ovs的连接关系
	# 此处考虑第二种情况
	# 所ovs_part只有一个，则该ovs不需要与计算节点的出口ovs相连，
	# 若ovs_part数量多于1个，则每个ovs_part都需要与计算节点的出口ovs相连，且vlan tag为task的默认vlan tag
	for ovs in ovsList:
		ovs['ovs_status'] = 'ovs_status_wait'
		ovs['task_uuid'] = task['task_uuid']
		#ovs['id'] = mOVSService.addNewOVS(ovs)
		ovs['ovs_parts'] = []
		for link in topologys:
			ovs_parts = ovs['ovs_parts']
			ovs_idx = 0
			if link[ovs_idx]['type'] != 'ovs' and link[1 - ovs_idx]['type'] == 'ovs':
				ovs_idx = 1 - ovs_idx
			if link[ovs_idx]['name'] == ovs['ovs_name'] and link[1 - ovs_idx]['type'] == 'vm':
				#先考虑与vm相连的情况
				vm = findVMByName(link[1 - ovs_idx]['name'], vmList)
				#检测是否在该host上有ovs_part
				ovs_part = None
				for part in ovs_parts:
					if part['host_uuid'] == vm['host_uuid']:
						ovs_part = part
						break
				if ovs_part is None:
					#创建新的ovs_part
					ovs_part = {}
					ovs_part['ovs_part_uuid'] = str(int(time.time())) + str(random.randrange(100,1000))
					ovs_part['ovs_uuid'] = ovs['ovs_uuid']
					ovs_part['ovs_part_status'] = 'ovs_part_status_wait'
					ovs_part['host_uuid'] = vm['host_uuid']
					ovs_parts.append(ovs_part)
					#新增端口信息
					port = {}
					port['port_uuid'] = str(int((time.time())))  + str(random.randrange(100, 1000))
					port['device_uuid'] = ovs_part['ovs_part_uuid']
					port['port_type'] = 'type_ovs'
					port['vlan_tag'] = link[ovs_idx]['vlan_tag']
					port['used'] = False
					if ovs_part.get('ovs_part_ports') is None:
						ovs_part['ovs_part_ports'] = []
					ovs_part['ovs_part_ports'].append(port)

					#创建vm到ovs的连接
					necessaryLink = {}
					necessaryLink['link_uuid'] = str(int(time.time())) + str(random.randrange(100,1000))
					necessaryLink['task_uuid'] = task['task_uuid']
					necessaryLink['link_status'] = 'link_status_wait'
					necessaryLink['link_port1_uuid'] = port['port_uuid']
					port['used'] = True
					vmPort = getFirstUnusedInterfaceForVM(vm)
					if vmPort is None:
						Log.e('error, vm port is None')
						raise Exception
					vmPort['used'] = True
					necessaryLink['link_port2_uuid'] = vmPort['port_uuid']
					necessaryLinks.append(necessaryLink)

		ovs['ovs_parts'] = ovs_parts
	#for ovs in ovsList:
	#	print '+++++++++++++++++++++++++++++++++++++++++++++++++++++++'
	#	for part in ovs['ovs_parts']:
	#		print part
	#print '========================================================'
	#考虑ovs与ovs相连的情况
	for ovs in ovsList:
		for link in topologys:
			ovs_parts = ovs['ovs_parts']
			ovs_idx = 0
			if link[ovs_idx]['type'] == 'ovs' and link[ovs_idx]['name'] != ovs['ovs_name']:
				ovs_idx = 1 - ovs_idx
			if link[ovs_idx]['type'] == 'ovs' and link[ovs_idx]['name'] == ovs['ovs_name'] and link[1 - ovs_idx]['type'] == 'ovs':
				ovs_2 = findOVSByName(link[1 - ovs_idx]['name'], ovsList)
				if ovs_2['ovs_name'] == ovs['ovs_name']:
					continue
				#print '---------------------in loop----------------------------'
				#print link
				if isLocateInSameHost(ovs['ovs_parts'], ovs_2['ovs_parts']) == False:
					hosts_for_ovs = hostForOVS(ovs)
					hosts_for_ovs_2 = hostForOVS(ovs_2)
					if len(hosts_for_ovs) == 0 and len(hosts_for_ovs_2) != 0:
						#在ovs中增加一个ovs_part，host为ovs_2中的任意一个host
						ovs_part = {}
						ovs_part['ovs_part_uuid'] = str(int(time.time())) + str(random.randrange(100,1000))
						ovs_part['ovs_uuid'] = ovs['ovs_uuid']
						ovs_part['ovs_part_status'] = 'ovs_part_status_wait'
						ovs_part['host_uuid'] = ovs_2['ovs_parts'][0]['host_uuid']
						ovs['ovs_parts'].append(ovs_part)
					elif len(hosts_for_ovs) != 0 and len(hosts_for_ovs_2) == 0:
						#在ovs_2中增加一个ovs_part,host为ovs中的任意一个host
						ovs_part = {}
						ovs_part['ovs_part_uuid'] = str(int(time.time())) + str(random.randrange(100,1000))
						ovs_part['ovs_uuid'] = ovs['ovs_uuid']
						ovs_part['ovs_part_status'] = 'ovs_part_status_wait'
						ovs_part['host_uuid'] = ovs['ovs_parts'][0]['host_uuid']
						ovs_2['ovs_parts'].append(ovs_part)
					elif len(hosts_for_ovs) > 0 and len(hosts_for_ovs_2) > 0:
						#在ovs中增加一个ovs_part，其host为ovs_2中的任一host
						ovs_part = {}
						ovs_part['ovs_part_uuid'] = str(int(time.time())) + str(random.randrange(100,1000))
						ovs_part['ovs_uuid'] = ovs['ovs_uuid']
						ovs_part['ovs_part_status'] = 'ovs_part_status_wait'
						ovs_part['host_uuid'] = ovs_2['ovs_parts'][0]['host_uuid']
						ovs['ovs_parts'].append(ovs_part)
					else:
						#在ovs和ovs_2中各增加一个ovs_part，host为任意一个host
						ovs_part = {}
						ovs_part['ovs_part_uuid'] = str(int(time.time())) + str(random.randrange(100,1000))
						ovs_part['ovs_uuid'] = ovs['ovs_uuid']
						ovs_part['ovs_part_status'] = 'ovs_part_status_wait'
						ovs_part['host_uuid'] = 'uuid_host_uuid'#任意一个host_uuid
						ovs['ovs_parts'].append(ovs_part)
						ovs_part = {}
						ovs_part['ovs_part_uuid'] = str(int(time.time())) + str(random.randrange(100,1000))
						ovs_part['ovs_uuid'] = ovs['ovs_uuid']
						ovs_part['ovs_part_status'] = 'ovs_part_status_wait'
						ovs_part['host_uuid'] = 'uuid_host_uuid'#任意一个host_uuid
						ovs_2['ovs_parts'].append(ovs_part)
				#在位于相同host上的ovs_part之间增加port和necessaryLink
				ovsPartTuple = findOVSPartInSameHost(ovs, ovs_2)
				#print '\ntuple[0]:'
				#print ovsPartTuple[0]
				#print '\ntuple[1]:'
				#print ovsPartTuple[1]
				if isOVSPartConnected(ovsPartTuple[0], ovsPartTuple[1], necessaryLinks) == True:
					continue
				ovs_part = ovsPartTuple[0]
				port1 = {}
				port1['port_uuid'] = str(int(time.time())) + str(random.randrange(100,1000))
				port1['port_type'] = 'type_ovs_part'
				port1['vlan_tag'] = link[1-ovs_idx]['vlan_tag']
				port1['device_uuid'] = ovs_part['ovs_part_uuid']
				port1['used'] = False
				if ovs_part.get('ovs_part_ports') is None:
					ovs_part['ovs_part_ports'] = []
				ovs_part['ovs_part_ports'].append(port1)
				
				ovs_2_part = ovsPartTuple[1]
				port2 = {}
				port2['port_uuid'] = str(int(time.time())) + str(random.randrange(100,1000))
				port2['port_type'] = 'type_ovs_part'
				port2['vlan_tag'] = link[ovs_idx]['vlan_tag']
				port2['device_uuid'] = ovs_2_part['ovs_part_uuid']
				port2['used'] = False
				if ovs_2_part.get('ovs_part_ports') is None:
					ovs_2_part['ovs_part_ports'] = []
				ovs_2_part['ovs_part_ports'].append(port2)

				#添加link信息
				necessaryLink = {}
				necessaryLink['link_uuid'] = str(int(time.time())) + str(random.randrange(100,1000))
				necessaryLink['task_uuid'] = task['task_uuid']
				necessaryLink['link_status'] = 'link_status_wait'
				necessaryLink['link_port1_uuid'] = port1['port_uuid']
				port1['used'] = True
				necessaryLink['link_port2_uuid'] = port2['port_uuid']
				port2['used'] = True
				necessaryLinks.append(necessaryLink)

	print '\njson dumps'
	for ovs in ovsList:
		print json.dumps(ovs)
	#将ovs,ovs_part,port,link写入数据库，提交任务并等待任务执行结束	
	mOVSService = OVSService.OVSService(config)
	mPortService = PortService.PortService(config)
	for ovs in ovsList:
		mOVSService.addNewOVS(ovs)
		for part in ovs['ovs_parts']:
			print part



#判断port_uuid是否属于给定的ovs_part
def isContainPort(ovs_part, port_uuid):
	result = False
	if ovs_part.get('ovs_part_ports') is None:
		return False
	for port in ovs_part['ovs_part_ports']:
		if port['port_uuid'] == port_uuid:
			result = True
			break
	return result

#根据给出的link信息判断两个ovs_part是否已经有link将它们相连
def isOVSPartConnected(ovs_part1, ovs_part2, links):
	isConnected = False
	for link in links:
		port1_uuid = link['link_port1_uuid']
		port2_uuid = link['link_port2_uuid']
		if isContainPort(ovs_part1, port1_uuid) and isContainPort(ovs_part2, port2_uuid):
			isConnected = True
			break
		elif isContainPort(ovs_part1, port2_uuid) and isContainPort(ovs_part2, port1_uuid):
			isConnected = True
			break
	return isConnected
		


#在vm列表中根据vm的名字取出对应的vm记录
def findVMByName(name, vms):
	for vm in vms:
		if vm['vm_name'] == name:
			return vm
	return None


#根据ovs名字查找对应的元素
def findOVSByName(name, ovsList):
	for ovs in ovsList:
		if ovs['ovs_name'] == name:
			return ovs
	return None

#获取ovs所使用的host列表
def hostForOVS(ovs):
	host = []
	for part in ovs['ovs_parts']:
		host.append(part['host_uuid'])
	return host

#判断两个数组是否含有相同值的元素
def isLocateInSameHost(ovs_parts1, ovs_parts2):
	for part1 in ovs_parts1:
		for part2 in ovs_parts2:
			if part1['host_uuid'] == part2['host_uuid']:
				return True
	return False

#获取两个ovs位于同一host上的ovs_part,并返回
def findOVSPartInSameHost(ovs1, ovs2):
	for part1 in ovs1['ovs_parts']:
		for part2 in ovs2['ovs_parts']:
			if part1['host_uuid'] == part2['host_uuid']:
				return [part1, part2]
	return None









#execute main function
if __name__ == '__main__':
	main()
	#project.help()

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
import httplib
import urllib

from utils import config as CONFIG
from utils import log as Log
from service import TaskService as TaskService
from service import VMService as VMService
from service import OVSService as OVSService




	
	
cfg = CONFIG.getConfig()
#gmWorker = gearman.GearmanWorker([cfg.get('gearman', 'server')])

"""
gearman workers method
"""
def createVirtualMachine(gearman_worker, gearman_job):
	#print gearman_job
	vm_uuid = gearman_job
	mVMService = VMService.VMService(cfg)

	#vm = mVMService.getVMByUUID(vm_uuid)
	#print vm
	#创建一个子进程完成任务
	pid = os.fork()
	if pid == 0:
		#子进程
		#serverStatus = _doCreate('vm_test', 'TestVM', '6')
		print 'from child' + str(pid)
		#结束子进程
		os._exit(0)
	else:
		#父进程，等待子进程结束
		result = os.wait()
		print result

	if serverStatus is None:
		Log.e('create vm failed')
	elif serverStatus == 'error':
		Log.e('create vm error')
	else:
		Log.e('create vm success')
	
	return ''


def _doCreate(vm_name, vm_image, vm_flavor, vm_host = None):
	NOVA_HOST = cfg.get('nova', 'nova_host')
	httpClient = None
	try:
		"""
		获取token
		curl -i http://172.16.0.2:5000/v2.0/tokens 
		-X POST 
		-H "Content-Type: application/json" 
		-H "Accept: application/json" 
		-H "User-Agent: python-novaclient" 
		-d '{"auth": {"tenantName": "admin", "passwordCredentials": {"username": "admin", "password": "admin"}}}'
		"""
		#params = urllib.urlencode({'{"auth": {"tenantName": "admin", "passwordCredentials": {"username": "admin", "password": "admin"}}}'})
		#params = urllib.urlencode()
		headers = {"Content-type": "application/json", 
					"Accept": "text/json", 
					"User-Agent":"python-novaclient"}
		httpClient = httplib.HTTPConnection(NOVA_HOST, 5000, timeout=30)
		httpClient.request("POST", "/v2.0/tokens", '{"auth": {"tenantName": "admin", "passwordCredentials": {"username": "admin", "password": "admin"}}}', headers)
		response = httpClient.getresponse()
		if int(response.status) != 200:
			raise Exception
		#print response.status
		#print response.reason
		#print response.getheaders() #获取头信息
		rspBody = json.loads(response.read())
		token = rspBody['access']['token']['id']
	
	
		"""
		获取image的id
		REQ: curl -i http://172.16.0.2:8774/v2/5114c16c3e2d496281c79b2a2ee67910/images 
		-X GET 
		-H "X-Auth-Project-Id: admin" 
		-H "User-Agent: python-novaclient" 
		-H "Accept: application/json" 
		-H "X-Auth-Token: 6d25bb310e2940f79772a47f319706fc"
		"""
		headers = {'X-Auth-Project-Id':'admin',
					'User-Agent': 'Python-novaclient',
					'Accept': 'application/json', 
					'X-Auth-Token': token}
		httpClient = httplib.HTTPConnection(NOVA_HOST, 8774, timeout = 30)
		httpClient.request('GET', '/v2/5114c16c3e2d496281c79b2a2ee67910/images', '', headers)
		response = httpClient.getresponse()
		if int(response.status) != 200:
			raise Exception
		#print response.reason
		#print response.getheaders()
		body = json.loads(response.read())
		imageID = None
		for image in body['images']:
			if image['id'] == vm_image or image['name'] == vm_image:
				imageID = image['id']
				break
		if imageID is None:
			Log.e('cannot find image')
			raise Exception('cannot find image')
		Log.d(imageID)
		"""
		获取镜像的详细信息
		REQ: curl -i http://172.16.0.2:8774/v2/5114c16c3e2d496281c79b2a2ee67910/images/72791779-456e-4bdf-a95f-4b0f1ec170b1 
		-X GET 
		-H "X-Auth-Project-Id: admin" 
		-H "User-Agent: python-novaclient" 
		-H "Accept: application/json" 
		-H "X-Auth-Token: 6d25bb310e2940f79772a47f319706fc
		"""
		httpClient = httplib.HTTPConnection(NOVA_HOST, 8774, timeout = 30)
		httpClient.request('GET', '/v2/5114c16c3e2d496281c79b2a2ee67910/images/' + imageID, '', headers)
		response = httpClient.getresponse()
		if int(response.status) != 200:
			Log.e('fetch image details failed. status is ' + str(response.status))
			raise Exception
		body = json.loads(response.read())

		"""
		获取配置信息
		REQ: curl -i http://172.16.0.2:8774/v2/5114c16c3e2d496281c79b2a2ee67910/flavors/6 
		-X GET 
		-H "X-Auth-Project-Id: admin" 
		-H "User-Agent: python-novaclient" 
		-H "Accept: application/json" 
		-H "X-Auth-Token: 6d25bb310e2940f79772a47f319706fc"
		"""
		httpClient = httplib.HTTPConnection(NOVA_HOST, 8774, timeout = 30)
		httpClient.request('GET', '/v2/5114c16c3e2d496281c79b2a2ee67910/flavors', '', headers)
		response = httpClient.getresponse()
		#print response.status
		#print response.reason
		#print response.getheaders()
		flavors = json.loads(response.read())
		#print flavors
		flavorID = None
		for flavor in flavors['flavors']:
			#print flavor
			if flavor['id'] == vm_flavor or flavor['name'] == vm_flavor:
				flavorID = flavor['id']
				break
		if flavorID is None:
			Log.e('cannot find flavor. falvor is ' + str(vm_flavor))
			raise Exception


		"""
		创建虚拟机
		REQ: curl -i http://172.16.0.2:8774/v2/5114c16c3e2d496281c79b2a2ee67910/servers 
		-X POST 
		-H "X-Auth-Project-Id: admin" 
		-H "User-Agent: python-novaclient" 
		-H "Content-Type: application/json" 
		-H "Accept: application/json" 
		-H "X-Auth-Token: 137a7fa9c13841419b1401e524bc4127" 
		-d '{"server": {"min_count": 1, "flavorRef": "6", "name": "vm4", "imageRef": "72791    779-456e-4bdf-a95f-4b0f1ec170b1", "max_count": 1}}'
		"""
		headers = {'X-Auth-Project-Id':'admin',
					'User-Agent': 'Python-novaclient',
					'Content-Type': 'application/json',
					'Accept': 'application/json', 
					'X-Auth-Token': token}
		httpClient = httplib.HTTPConnection(NOVA_HOST, 8774, timeout = 30)
		httpClient.request('POST', '/v2/5114c16c3e2d496281c79b2a2ee67910/servers', 
						'{"server": {"min_count": 1, "flavorRef": "' + flavorID + '", "name": "' + vm_name + '", "imageRef": "' + imageID + '", "max_count": 1}}', 
						headers)
		response = httpClient.getresponse()
		#print response.status
		#print response.reason
		#print response.getheaders()
		server = json.loads(response.read())
		serverID = server['server']['id']
		if serverID is None:
			Log.e('returned server id is None')
			raise Exception
		"""
		查询server状态
		REQ: curl -i http://172.16.0.2:8774/v2/5114c16c3e2d496281c79b2a2ee67910/servers/38590b0e-f683-43f6-8369-bb92096d415c 
		-X GET 
		-H "X-Auth-Project-Id: admin" 
		-H "User-Agent: python-novaclient" 
		-H "Accept: application/json" 
		-H "X-Auth-Token: 137a7fa9c13841419b1401e524bc4127"
		"""
		serverStatus = None
		while(True):
			time.sleep(1)
			headers = {'X-Auth-Project-ID': 'admin',
					   'User-Agent': 'python-novaclient',
					   'Accept': 'application/json', 
					   'X-Auth-Token': token}
			httpClient = httplib.HTTPConnection(NOVA_HOST, 8774, timeout = 30)
			httpClient.request('GET', '/v2/5114c16c3e2d496281c79b2a2ee67910/servers/' + serverID, '', headers)
			response = httpClient.getresponse()
			#print response.status
			#print response.reason
			#print response.getheaders()
			server = json.loads(response.read())
			print '\n' + json.dumps(server) + '\n'
			serverStatus = server['server']['status'].lower()

			if serverStatus == 'error' or serverStatus == 'active':
				Log.d('finish. status is ' + serverStatus)
				break;
			else:
				Log.d('wait. status is ' + serverStatus)
		
		return serverStatus	
	except Exception as e:
		print 'error'
	finally:
		if httpClient:
			httpClient.close()

#gmWorker.register_task('createVirtualMachine', createVirtualMachine)

#gmWorker.work()






#execute main function
if __name__ == '__main__':
	createVirtualMachine('', '1403769810852')

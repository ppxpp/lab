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






#def main():
#	return
	
	
cfg = CONFIG.getConfig()
#gmWorker = gearman.GearmanWorker([cfg.get('gearman', 'server')])

"""
gearman workers method
"""
def createVirtualMachine(gearman_worker, gearman_job):
	#print gearman_job
	vm_uuid = gearman_job
	mVMService = VMService.VMService(cfg)

	vm = mVMService.getVMByUUID(vm_uuid)
	#print vm
	_doCreate('vm_test', 'TestVM', '6')
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
			print 'status is ' + str(response.status)
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
			print 'status is ' + str(response.status)
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
			raise Exception
		print imageID
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
		print response.status
		print response.reason
		print response.getheaders()
		print response.read()

		
	
	except Exception, e:
		print e
	finally:
		if httpClient:
			httpClient.close()

#gmWorker.register_task('createVirtualMachine', createVirtualMachine)

#gmWorker.work()






#execute main function
if __name__ == '__main__':
	createVirtualMachine('', '1403769810852')

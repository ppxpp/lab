#!/usr/bin/env python
#coding=utf8


import json
import httplib, urllib
  
httpClient = None
try:

	NOVA_IP = '172.16.0.2'

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
	httpClient = httplib.HTTPConnection(NOVA_IP, 5000, timeout=30)
	httpClient.request("POST", "/v2.0/tokens", '{"auth": {"tenantName": "admin", "passwordCredentials": {"username": "admin", "password": "admin"}}}', headers)
	response = httpClient.getresponse()
	if int(response.status) != 200:
		print 'status is ' + response.status
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
	httpClient = httplib.HTTPConnection(NOVA_IP, 8774, timeout = 30)
	httpClient.request('GET', '/v2/5114c16c3e2d496281c79b2a2ee67910/images', '', headers)
	response = httpClient.getresponse()
	#if int(response.status) != 200:
	#	print 'status is ' + response.status
	#	raise Exception
	print response.status
	print response.reason
	print response.getheaders()
	body = json.loads(response.read())
	for image in body['images']:
		print image

except Exception, e:
	print e
finally:
	if httpClient:
		httpClient.close()

#!/usr/bin/env python
#coding=utf-8

import json
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest
from aliyunsdkecs.request.v20140526.DescribeDisksRequest import DescribeDisksRequest

accessKeyId = 'xxxx'
accessSecret = 'xxxx'
regionId = 'cn-beijing'

def get_instance_disk_info(instance_id):
    disk_infos = ''
    client = AcsClient(accessKeyId, accessSecret, regionId)
    request = DescribeDisksRequest()
    request.set_accept_format('json')
    request.set_InstanceId(instance_id)
    d_response = client.do_action_with_exception(request)
    d_res = json.loads(str(d_response, encoding='utf-8'))
    for disk in d_res['Disks']['Disk']:
        disk_infos += disk['Device'] + ': ' + str(disk['Size']) + 'GB' + ' '
    return disk_infos

def get_aliecs_info(instance_id):
    client = AcsClient(accessKeyId, accessSecret, regionId)
    request = DescribeInstancesRequest()
    request.set_accept_format('json')
    instnce_id_data = []
    instnce_id_data.append(instance_id)
    # print(instnce_id_data)
    request.set_InstanceIds(instnce_id_data)
    response = client.do_action_with_exception(request)
    res = json.loads(str(response, encoding='utf-8'))
    disks_info = get_instance_disk_info(instance_id)
    # print(disks_info)
    res['disk_infos'] = disks_info
    return res

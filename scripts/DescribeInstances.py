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
Page_Size = 100
data = []


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

def get_page_numbers():
    client = AcsClient(accessKeyId, accessSecret, regionId)
    request = DescribeInstancesRequest()
    request.set_accept_format('json')
    PageSize = Page_Size
    request.set_PageSize(PageSize)

    response = client.do_action_with_exception(request)
    res = json.loads(str(response, encoding='utf-8'))

    Page_Number = res['TotalCount'] / PageSize  #3.77
    if type(Page_Number) is float:
        Page_Number = res['TotalCount'] // PageSize # 3
        Page_Number += 1
    else:
        Page_Number = Page_Number
    return Page_Number

def get_ali_ecs_info():
    Page_Number = get_page_numbers()
    start_step = 1
    end_step = Page_Number + 1

    for number in range(start_step, end_step):
        client = AcsClient(accessKeyId, accessSecret, regionId)
        request = DescribeInstancesRequest()
        request.set_accept_format('json')
        PageSize = Page_Size
        request.set_PageNumber(number)
        request.set_PageSize(PageSize)
        response = client.do_action_with_exception(request)
        res = json.loads(str(response, encoding='utf-8'))
        # print(res["Instances"]["Instance"][0].keys())
        instance_id = res["Instances"]["Instance"][0]["InstanceId"]
        # print(instance_id)
        disks_info = get_instance_disk_info(instance_id)
        for instance in res["Instances"]["Instance"]:
            instance['disk_infos'] = disks_info
            data.append(instance)
    # print(len(data))
    # instance_number = len(data)
    # return instance_number
    return data

if __name__ == '__main__':
    get_ali_ecs_info()

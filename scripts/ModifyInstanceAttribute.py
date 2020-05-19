#!/usr/bin/env python
#coding=utf-8

import json
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkecs.request.v20140526.ModifyInstanceAttributeRequest import ModifyInstanceAttributeRequest

accessKeyId = 'xxxx'
accessSecret = 'xxxx'
regionId = 'cn-beijing'

def ModifyInstance(InstanceId, HostName,
                   InstanceName, Description):

    # print(InstanceId, HostName, InstanceName, Description, regionId)
    client = AcsClient(accessKeyId, accessSecret, regionId)
    request = ModifyInstanceAttributeRequest()
    request.set_accept_format('json')

    request.set_InstanceId(InstanceId)
    request.set_HostName(HostName)
    request.set_InstanceName(InstanceName)
    request.set_Description(Description)

    response = client.do_action_with_exception(request)
    res = json.loads(str(response, encoding='utf-8'))
    print(res)
    if 'RequestId' in res:
        print('更新资产信息完成')
        return '更新资产信息完成'
    else:
        return res

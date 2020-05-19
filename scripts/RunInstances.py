#!/usr/bin/env python
#coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkecs.request.v20140526.RunInstancesRequest import RunInstancesRequest
import json

accessKeyId = 'xxxx'
accessSecret = 'xxxx'

#按量付费
def create_ali_ecs_PostPaid(ImageId, InstanceType,
                   SecurityGroupIds, VSwitchId,
                   InstanceName, Description,
                   HostName, ZoneId,
                   regionId, service_name, *args, **kwargs):
    # print(args)
    # print(kwargs)

    client = AcsClient(accessKeyId, accessSecret, regionId)
    request = RunInstancesRequest()
    request.set_accept_format('json')

    password = 'FW^L^NRMs7eh@jsPAv(iiKZU1K)wc'

    request.set_ImageId(ImageId)
    request.set_InstanceType(InstanceType)
    request.set_SecurityGroupIdss(SecurityGroupIds)
    request.set_VSwitchId(VSwitchId)
    request.set_InstanceName(InstanceName)
    request.set_Description(Description)
    request.set_HostName(HostName)
    request.set_Password(password)
    request.set_ZoneId(ZoneId)
    request.set_Amount(1)
    request.set_SecurityEnhancementStrategy("Active")

    request.set_Tags([
      {
        "Key": "group",
        "Value": service_name
      }
    ])


    for kwarg in kwargs:
        # 判断数据盘指定与否
        if 'datadisk' in kwarg:
            DataDisk = kwargs['datadisk']['datadisk']

            request.set_DataDisks([
                {
                    "Size": DataDisk,
                    "Category": "cloud_ssd"
                }
            ])

    request.set_InstanceChargeType("PostPaid")

    response = client.do_action_with_exception(request)
    res = json.loads(str(response, encoding='utf-8'))
    return res

#包年包月
def create_ali_ecs_PrePaid(ImageId, InstanceType,
                   SecurityGroupIds, VSwitchId,
                   InstanceName, Description,
                   HostName, ZoneId,
                   regionId, service_name, PeriodUnit, *args, **kwargs):

    print(args)
    print(kwargs)

    client = AcsClient(accessKeyId, accessSecret, regionId)
    request = RunInstancesRequest()
    request.set_accept_format('json')

    password = 'xxxxxxx'

    request.set_ImageId(ImageId)
    request.set_InstanceType(InstanceType)
    request.set_SecurityGroupIdss(SecurityGroupIds)
    request.set_VSwitchId(VSwitchId)
    request.set_InstanceName(InstanceName)
    request.set_Description(Description)
    request.set_HostName(HostName)
    request.set_Password(password)
    request.set_ZoneId(ZoneId)
    request.set_Amount(1)
    request.set_SecurityEnhancementStrategy("Active")

    request.set_Tags([
      {
        "Key": "group",
        "Value": service_name
      }
    ])

    for kwarg in kwargs:
        # 判断数据盘指定与否
        if 'datadisk' in kwarg:
            DataDisk = kwargs['datadisk']
            request.set_DataDisks([
                {
                    "Size": DataDisk,
                    "Category": "cloud_ssd"
                }
            ])

    request.set_Period(1)
    request.set_PeriodUnit(PeriodUnit)
    request.set_AutoRenew(True)
    request.set_AutoRenewPeriod(1)
    request.set_InstanceChargeType("PrePaid")

    response = client.do_action_with_exception(request)
    res = json.loads(str(response, encoding='utf-8'))
    return res

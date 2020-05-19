#!/usr/bin/env python
#coding=utf-8

import json
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkecs.request.v20140526.DescribeAvailableResourceRequest import DescribeAvailableResourceRequest
from aliyunsdkecs.request.v20140526.DescribeInstanceTypesRequest import DescribeInstanceTypesRequest

accessKeyId = 'xxxx'
accessSecret = 'xxxx'
regionId = 'cn-beijing'

def get_InsType_infos():
    InsTypeclient = AcsClient(accessKeyId, accessSecret, regionId)

    request = DescribeInstanceTypesRequest()
    request.set_accept_format('json')

    response = InsTypeclient.do_action_with_exception(request)
    res_InsType = json.loads(str(response, encoding='utf-8'))
    return res_InsType


def get_AvailableResource(ChargeType):
    availableresourceclient = AcsClient(accessKeyId, accessSecret, regionId)
    request = DescribeAvailableResourceRequest()
    request.set_accept_format('json')

    request.set_DestinationResource("InstanceType")
    request.set_InstanceChargeType(ChargeType)
    request.set_SpotStrategy("NoSpot")
    request.set_IoOptimized("optimized")
    request.set_SystemDiskCategory("cloud_efficiency")
    request.set_DataDiskCategory("cloud_ssd")
    request.set_NetworkCategory("vpc")
    request.set_ResourceType("instance")

    response = availableresourceclient.do_action_with_exception(request)
    res_available = json.loads(str(response, encoding='utf-8'))
    # res_available['AvailableZones']['AvailableZone'][0]
    # ['AvailableResources']['AvailableResource']
    # [0]['SupportedResources']['SupportedResource']
    # [0].keys()


    availablezones = res_available['AvailableZones']['AvailableZone']

    res_instype = get_InsType_infos()

    instype_list = []
    for availablezone in availablezones:
        zoneid = availablezone['ZoneId']
        # print(zoneid)
        availableresources = availablezone['AvailableResources']['AvailableResource']
        for availableresource in availableresources:
            supportedresources = availableresource['SupportedResources']['SupportedResource']
            for supportedresource in supportedresources:
                instype_dict = {}
                for InsType in res_instype['InstanceTypes']['InstanceType']:

                    '''
                    WithStock：库存充足
                    ClosedWithStock：库存供应保障能力低，请优先选用WithStock状态的产品规格
                    WithoutStock：库存告罄
                    '''

                    # if supportedresource['StatusCategory'] == 'WithStock':
                    if supportedresource['Value'] == InsType['InstanceTypeId']:

                        '''
                        t5 & t6 是突发性实例类型
                        '''

                        if 't5' not in supportedresource['Value'] and 't6' not in supportedresource['Value']:
                            cpucorecount = InsType['CpuCoreCount']
                            memorysize = InsType['MemorySize']
                            typename = InsType['InstanceTypeId']
                            instype_dict['CpuCoreCount'] = cpucorecount
                            instype_dict['MemorySize'] = memorysize
                            instype_dict['typename'] = typename
                            instype_dict['zoneid'] = zoneid
                            instype_dict['chargetype'] = ChargeType
                            instype_list.append(instype_dict)
    # print(instype_list)
    # print(len(instype_list))
    return instype_list

#!/usr/bin/env python
#coding=utf-8
import json
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkecs.request.v20140526.DescribeVpcsRequest import DescribeVpcsRequest
from aliyunsdkecs.request.v20140526.DescribeVSwitchesRequest import DescribeVSwitchesRequest
from aliyunsdkecs.request.v20140526.DescribeSecurityGroupsRequest import DescribeSecurityGroupsRequest

accessKeyId = 'xxxx'
accessSecret = 'xxxx'
regionId = 'cn-beijing'

res_list = []

# 数据结构
# [{
#           "vpcid": "xxx",
# 			"vpcname": "xxx",
# 			"switches ": [{
# 				"switch1 ": "xx "
# 			}, {
# 				"switch2 ": "xx "
# 			}],
# 			"segs ": [{
# 				"seg1 ": "xx"
# 			}, {
# 				"seg2 ": "xx"
# 			}]
# 	},
# 	{
#           "vpcid": "xxx",
# 			"vpcname": "xxx",
# 			"switches ": [{
# 				"switch1 ": "xx"
# 			}, {
# 				"switch2 ": "xx"
# 			}],
# 			"segs ": [{
# 				"seg1 ": "xx"
# 			}, {
# 				"seg2 ": "xx"
# 			}]
# 	}
# ]

def get_vpc_infos():
    vpcclient = AcsClient(accessKeyId, accessSecret, regionId)
    request = DescribeVpcsRequest()
    request.set_accept_format('json')
    response = vpcclient.do_action_with_exception(request)
    res_vpc = json.loads(str(response, encoding='utf-8'))
    return res_vpc

def get_switch_infos(vpcid):
    switchclient = AcsClient(accessKeyId, accessSecret, regionId)
    request = DescribeVSwitchesRequest()
    request.set_accept_format('json')
    request.set_PageSize(50)
    request.set_VpcId(vpcid)
    response = switchclient.do_action_with_exception(request)
    res_switch = json.loads(str(response, encoding='utf-8'))
    return res_switch

def get_vpc_seg(vpcid):
    segclient = AcsClient(accessKeyId, accessSecret, regionId)
    request = DescribeSecurityGroupsRequest()
    request.set_accept_format('json')
    request.set_VpcId(vpcid)
    request.set_PageSize(50)
    request.set_NetworkType("vpc")
    response = segclient.do_action_with_exception(request)
    res_seg = json.loads(str(response, encoding='utf-8'))
    return res_seg

def get_vpc_switch_seg_infos():
    vpc_infos = get_vpc_infos()
    for vpc in vpc_infos['Vpcs']['Vpc']:

        res_dict = {}
        switch_list = []
        seg_list = []

        switch_infos = get_switch_infos(vpc['VpcId'])
        for switch_instance in switch_infos['VSwitches']['VSwitch']:
            switch_dict = {}
            switch_dict['VSwitchName'] = switch_instance['VSwitchName']
            switch_dict['ZoneId'] = switch_instance['ZoneId']
            switch_dict['VSwitchId'] = switch_instance['VSwitchId']
            switch_list.append(switch_dict)

        seg_infos = get_vpc_seg(vpc['VpcId'])
        for seg_instance in seg_infos['SecurityGroups']['SecurityGroup']:
            seg_dict = {}
            seg_dict['SecurityGroupName'] = seg_instance['SecurityGroupName']
            seg_dict['SecurityGroupId'] = seg_instance['SecurityGroupId']
            seg_list.append(seg_dict)


        res_dict['VpcId'] = vpc['VpcId']
        res_dict['RegionId'] = vpc['RegionId']
        res_dict['Vpcname'] = vpc['VpcName']
        res_dict['Switches'] = switch_list
        res_dict['Segs'] = seg_list
        res_list.append(res_dict)
    # print(res_list)
    return res_list

#         for switch in res_switch['VSwitches']['VSwitch']:
#             res_dict = {}
#             res_dict['Vpcname'] = vpc['VpcName']
#             res_dict['VpcId'] = vpc['VpcId']
#             res_dict['VSwitchId'] = switch['VSwitchId']
#             res_dict['VSwitchName'] = switch['VSwitchName']
#             res_list.append(res_dict)
# print(res_list)
if __name__ == '__main__':
    get_vpc_switch_seg_infos()

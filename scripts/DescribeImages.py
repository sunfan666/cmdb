#!/usr/bin/env python
#coding=utf-8
import json
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkecs.request.v20140526.DescribeImagesRequest import DescribeImagesRequest
accessKeyId = 'xxxx'
accessSecret = 'xxxx'
regionId = 'cn-beijing'

def get_image_infos():
    imageclient = AcsClient(accessKeyId, accessSecret, regionId)
    request = DescribeImagesRequest()
    request.set_accept_format('json')
    request.set_PageSize(100)
    request.set_OSType("linux")
    request.set_Architecture("x86_64")
    # request.set_Usage("instance")
    request.set_ActionType("CreateEcs")
    response = imageclient.do_action_with_exception(request)
    res_image = json.loads(str(response, encoding='utf-8'))
    image_list = []
    for image in res_image['Images']['Image']:
        image_dict = {}
        image_dict['imageid'] = image['ImageId']
        image_dict['imageowner'] = image['ImageOwnerAlias']
        image_dict['name'] = image['ImageName']
        image_list.append(image_dict)
    # print(image_list)
    return image_list

if __name__ == '__main__':
    get_image_infos()

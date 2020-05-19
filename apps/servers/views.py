from rest_framework import mixins, viewsets, permissions, response, status
from django.db.models.query import QuerySet


from django.core.exceptions import ValidationError
from django.db.models.query import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import mixins, views
from rest_framework.settings import api_settings

from .models import Server, NetworkDevice, IP
from vpcs.models import Vpcs, Switches, SecurityGroups, Images, AvailableResources, ResourceMatching
from idcs.models import Idc
from cabinet.models import Cabinet
from products.models import Product
from .serializers import ServerSerializer, ServerListSerializer, \
    NetworkDeviceSerializer, IPSerializer, AutoReportSerializer
from .filter import ServerFilter, NetworkDeviceFilter, IpFilter
from .filters import ServerListFilter
from scripts.DescribeInstances import get_ali_ecs_info
from scripts.DescribeInstances2 import get_aliecs_info
from scripts.RunInstances import create_ali_ecs_PostPaid, create_ali_ecs_PrePaid
from scripts.DescribeVpcs import get_vpc_switch_seg_infos
from scripts.DescribeImages import get_image_infos
from scripts.ModifyInstanceAttribute import ModifyInstance
from scripts.DescribeInstanceTypes import get_AvailableResource

import random
import string
import logging
logger = logging.getLogger(__name__)

# class ServerViewset(viewsets.ReadOnlyModelViewSet,
#                     mixins.UpdateModelMixin,
#                     mixins.DestroyModelMixin):

class AddIdcViewset(mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer

    filter_class = ServerFilter
    filter_fields = ('hostname', 'idc', 'cabinet', "service", "server_purpose", "server_type")

class ServerViewset(viewsets.ModelViewSet):

    """
    list:
    获取服务器列表

    retrieve:
    获取指定服务器记录

    create:
    创建服务器记录

    update:
    修改服务器记录

    delete:
    删除服务器记录
    """
    queryset = Server.objects.all()
    serializer_class = ServerSerializer
    #extra_perms_map = {
    #    "GET": ["products.view_product"]
    #}
    filter_class = ServerFilter
    filter_fields = ('hostname', 'idc', 'cabinet', "service", "server_purpose", "server_type", "remark")

    # def get_queryset(self):
    #     queryset = super(ServerViewset, self).get_queryset()
    #     queryset = queryset.order_by("id")
    #     return queryset

    # def update(self, request, *args, **kwargs):
    #     partial = kwargs.pop('partial', False)
    #     instance = self.get_object()
    #     # print(request.data)
    #     data = get_ali_ecs_info()
    #     for instance_ip_info in data:
    #         if "NetworkInterfaces" in instance_ip_info.keys():
    #             aliyun_ip = instance_ip_info['NetworkInterfaces']["NetworkInterface"][0]['PrimaryIpAddress']
    #             if request.data['ip'] == aliyun_ip:
    #                 request.data['status'] = instance_ip_info['Status']
    #                 request.data['instance_id'] = instance_ip_info['InstanceId']
    #                 request.data['cpu_core_count'] = instance_ip_info['Cpu']
    #     # if request.data['ip'] == data
    #     # n = get_ali_ecs_info()
    #     # m = get_page_numbers()
    #     # print(n)
    #     # print(m)
    #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #
    #     if getattr(instance, '_prefetched_objects_cache', None):
    #         # If 'prefetch_related' has been applied to a queryset, we need to
    #         # forcibly invalidate the prefetch cache on the instance.
    #         instance._prefetched_objects_cache = {}
    #
    # return response.Response(serializer.data)

    def create(self, request, *args, **kwargs):
        print(request.data)
        # 首先判断备注的传值是不是已经存在
        remark = request.data['remark']
        try:
            res = Server.objects.all().filter(remark=remark)
            if res.count() != 0:

                data = {
                    "detail": '备注已经存在',
                }

                return response.Response(data, status=status.HTTP_400_BAD_REQUEST)
            else:
                pass
        except Server.DoesNotExist:
            pass
        # --------正式创建云主机-------
        # print(request.data)
        InstanceType_id = request.data['InstanceType']
        InstanceTypeobj = AvailableResources.objects.filter(id__exact=InstanceType_id)
        InstanceType    = InstanceTypeobj.values()[0]['typename']

        ChargeType = request.data['ChargeType']

        if ChargeType == '按量付费':
            vpcid = request.data['VpcId']
            vpcobj = Vpcs.objects.filter(id__exact=vpcid)
            #######################################
            #                                     #
            #  先在阿里云上创建完毕，取出所需字段值     #
            #  写入数据库                           #
            #                                     #
            #######################################
            # 处理 IDC 与 阿里云地域的匹配
            idcid = request.data['idc']
            idcobj = Idc.objects.filter(id__exact=idcid)
            regionId = idcobj.values()[0]['letter']

            # 处理 机柜 与 地域分区的匹配
            cabinetid = request.data['cabinet']
            cabinetobj = Cabinet.objects.filter(id__exact=cabinetid)
            ZoneId = cabinetobj.values()[0]['letter']

            Image_Id = request.data['image']
            ImageId = Images.objects.get(id=Image_Id).imageid

            SecurityGroupIds = []
            for SecurityGroup_Id in request.data['SecurityGroupId']:
                SecurityGroupId = SecurityGroups.objects.get(id=SecurityGroup_Id).segid
                SecurityGroupIds.append(SecurityGroupId)
            # print(SecurityGroupIds)

            # SecurityGroup_Id = request.data['SecurityGroupId']
            # SecurityGroupId = SecurityGroups.objects.get(id=SecurityGroup_Id).segid

            VSwitch_Id = request.data['VSwitchId']
            VSwitchId = Switches.objects.get(id=VSwitch_Id).switchid

            InstanceName = request.data['InstanceName']

            #默认随机主机名
            RandomHostName = ''.join(random.sample(string.ascii_letters, 10))
            Description = RandomHostName
            HostName = RandomHostName

            service_id = request.data['service']
            service_name = Product.objects.get(id=service_id).service_name

            if 'datadisk' in request.data:
                datadisk = {}
                datadisk['datadisk'] = request.data['datadisk']
                ali_create_data = create_ali_ecs_PostPaid(ImageId=ImageId, InstanceType=InstanceType,
                                                SecurityGroupIds=SecurityGroupIds, VSwitchId=VSwitchId,
                                                InstanceName=InstanceName, Description=Description,
                                                HostName=HostName, ZoneId=ZoneId, regionId=regionId,
                                                service_name=service_name, datadisk=datadisk)
            else:
                ali_create_data = create_ali_ecs_PostPaid(ImageId=ImageId, InstanceType=InstanceType,
                                                SecurityGroupIds=SecurityGroupIds, VSwitchId=VSwitchId,
                                                InstanceName=InstanceName, Description=Description,
                                                HostName=HostName, ZoneId=ZoneId, regionId=regionId,
                                                service_name=service_name)
            # 通过实例 ID 找到实例 IP 地址，然后传值给 request.data 将整条数据条目写入数据库
            # print(ali_create_data['InstanceIdSets']['InstanceIdSet'])
            instanceID = ali_create_data['InstanceIdSets']['InstanceIdSet'][0]
            # 这里注意一下，不是马上就能拿到 ECS 信息，需要等待一段时间。默认赋值 10 秒。
            import time
            time.sleep(10)

            instanceDescribe = get_aliecs_info(instanceID)
            # print(instanceDescribe)
            all_ecs_infos = instanceDescribe['Instances']['Instance'][0]
            instanceIp = all_ecs_infos['NetworkInterfaces']["NetworkInterface"][0]['PrimaryIpAddress']

            # 更新主机名到阿里云
            server_purpose_id = request.data['server_purpose']
            server_purpose_name = Product.objects.get(id=server_purpose_id).service_name
            # 阿里云主机名不支持有下划线的存在 应用名称中可能有下划线  需要把下划线转为横杠
            Hostname = str(service_name) + '-' + str(server_purpose_name) + '-' + str(instanceIp)+'.ali'
            HostName = Hostname.lower().replace("_", "-")
            # print(HostName)
            ModifyInstance(InstanceId=instanceID, HostName=HostName,
                           InstanceName=InstanceName, Description=InstanceName)
            #将更新后的主机名信息写入资产系统
            request.data['hostname'] = HostName
            request.data['ip'] = instanceIp
            request.data['instance_id'] = instanceID
            request.data['ImageId'] = ImageId
            request.data['InstanceType'] = InstanceType
            request.data['SecurityGroupIds'] = str(SecurityGroupIds)
            request.data['VSwitchId'] = VSwitchId
            # print(instanceIp)
            # print(request.data)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        elif ChargeType == '包年包月':
            vpcid = request.data['VpcId']
            vpcobj = Vpcs.objects.filter(id__exact=vpcid)
            #######################################
            #                                     #
            #  先在阿里云上创建完毕，取出所需字段值     #
            #  写入数据库                           #
            #                                     #
            #######################################
            # 处理 IDC 与 阿里云地域的匹配
            idcid = request.data['idc']
            idcobj = Idc.objects.filter(id__exact=idcid)
            regionId = idcobj.values()[0]['letter']
            # print(regionId)
            # print('xxxxxxxx')

            # 处理 机柜 与 地域分区的匹配
            cabinetid = request.data['cabinet']
            cabinetobj = Cabinet.objects.filter(id__exact=cabinetid)
            ZoneId = cabinetobj.values()[0]['letter']

            Image_Id = request.data['image']
            ImageId = Images.objects.get(id=Image_Id).imageid

            SecurityGroupIds = []
            for SecurityGroup_Id in request.data['SecurityGroupId']:
                SecurityGroupId = SecurityGroups.objects.get(id=SecurityGroup_Id).segid
                SecurityGroupIds.append(SecurityGroupId)
                # print(SecurityGroupIds)

            # SecurityGroup_Id = request.data['SecurityGroupId']
            # SecurityGroupId = SecurityGroups.objects.get(id=SecurityGroup_Id).segid

            VSwitch_Id = request.data['VSwitchId']
            VSwitchId = Switches.objects.get(id=VSwitch_Id).switchid

            InstanceName = request.data['InstanceName']

            # 默认随机主机名
            RandomHostName = ''.join(random.sample(string.ascii_letters, 10))
            Description = RandomHostName
            HostName = RandomHostName

            service_id = request.data['service']
            service_name = Product.objects.get(id=service_id).service_name

            PeriodUnit = request.data['PeriodUnit']

            if 'datadisk' in request.data:
                datadisk = request.data['datadisk']
                ali_create_data = create_ali_ecs_PrePaid(ImageId=ImageId, InstanceType=InstanceType,
                                                    SecurityGroupIds=SecurityGroupIds, VSwitchId=VSwitchId,
                                                    InstanceName=InstanceName, Description=Description,
                                                    HostName=HostName, ZoneId=ZoneId, regionId=regionId,
                                                    service_name=service_name, datadisk=datadisk, PeriodUnit=PeriodUnit)
            else:
                ali_create_data = create_ali_ecs_PrePaid(ImageId=ImageId, InstanceType=InstanceType,
                                                    SecurityGroupIds=SecurityGroupIds, VSwitchId=VSwitchId,
                                                    InstanceName=InstanceName, Description=Description,
                                                    HostName=HostName, ZoneId=ZoneId, regionId=regionId,
                                                    service_name=service_name, PeriodUnit=PeriodUnit)
            # 通过实例 ID 找到实例 IP 地址，然后传值给 request.data 将整条数据条目写入数据库
            # print(ali_create_data['InstanceIdSets']['InstanceIdSet'])
            instanceID = ali_create_data['InstanceIdSets']['InstanceIdSet'][0]
            # 这里注意一下，不是马上就能拿到 ECS 信息，需要等待一段时间。默认赋值 10 秒。
            import time
            time.sleep(10)
            instanceDescribe = get_aliecs_info(instanceID)
            # print(instanceDescribe)
            all_ecs_infos = instanceDescribe['Instances']['Instance'][0]
            instanceIp = all_ecs_infos['NetworkInterfaces']["NetworkInterface"][0]['PrimaryIpAddress']

            # 更新主机名到阿里云
            server_purpose_id = request.data['server_purpose']
            server_purpose_name = Product.objects.get(id=server_purpose_id).service_name
            # 阿里云主机名不支持有下划线的存在  应用名称中可能有下划线  需要把下划线转为横杠
            Hostname = str(service_name) + '-' + str(server_purpose_name) + '-' + str(instanceIp) + '.ali'
            HostName = Hostname.lower().replace("_", "-")
            # print(HostName)
            ModifyInstance(InstanceId=instanceID, HostName=HostName,
                           InstanceName=InstanceName, Description=InstanceName)
            # print(instanceID, HostName)
            logger.debug('instanceid: %s; hostname: %s' % (instanceID, HostName))
            # 将更新后的主机名信息写入资产系统
            request.data['hostname'] = HostName
            request.data['ip'] = instanceIp
            request.data['instance_id'] = instanceID
            request.data['ImageId'] = ImageId
            request.data['InstanceType'] = InstanceType
            request.data['SecurityGroupIds'] = str(SecurityGroupIds)
            request.data['VSwitchId'] = VSwitchId

            # print(instanceIp)
            # print(request.data)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    def perform_create(self, serializer):
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    def get_queryset(self):
        queryset = super(ServerViewset, self).get_queryset()
        queryset = queryset.order_by("id")
        start    = self.request.query_params.get('start_time', None)
        stop     = self.request.query_params.get('end_time', None)
        if start and stop:
            # return queryset.filter(updated_time__gte=start).filter(updated_time__lte=stop)
            return queryset.filter(updated_time__range=(start, stop))
        return queryset

class flushServerInfoViewset(mixins.UpdateModelMixin,
                             mixins.ListModelMixin,
                             viewsets.GenericViewSet):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return response.Response(serializer.data)

    def get_object(self):
        """
        Returns the object the view is displaying.
        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def get_queryset(self):
        """
        Get the list of items for this view.
        This must be an iterable, and may be a queryset.
        Defaults to using `self.queryset`.
        This method should always be used rather than accessing `self.queryset`
        directly, as `self.queryset` gets evaluated only once, and those results
        are cached for all subsequent requests.
        You may want to override this if you need to provide different
        querysets depending on the incoming request.
        (Eg. return a list of items that is specific to the user)
        """
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )

        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        data = get_ali_ecs_info()
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        # print(len(serializer.data))
        for ins in serializer.data:
            # ins = dict(ins)
            # print(type(ins))
            # print(ins)
            # print(ins.keys())
            # print(ins['ip'])
            # print(serializer.data)
            for instance_ip_info in data:
                for instance in self.queryset:
                    if "NetworkInterfaces" in instance_ip_info.keys():
                        aliyun_ip = instance_ip_info['NetworkInterfaces']["NetworkInterface"][0]['PrimaryIpAddress']
                        if ins['ip'] == aliyun_ip:
                            if str(instance) == aliyun_ip:
                        # ins_d = dict(ins)
                    # if 'instance_id' in ins:
                    # if ins['instance_id'] == instance_ip_info['InstanceId']:
                    #     print(ins['instance_id'], instance_ip_info['InstanceId'], ins['ip'])
                        # print(instance_ip_info['InstanceId'])

                    # 不需要自动刷新的数据不要修改，不能动原始数据
                    #     for k, v in ins.items():
                    #         request.data[k] = v
                    #     print(request.data)
                    # 只修改部分数据为阿里云数据，
                                request.data['status'] = instance_ip_info['Status']
                                request.data['cpu_core_count'] = str(instance_ip_info['Cpu']) + ' Core'
                                request.data['server_mem'] = str(int(instance_ip_info['Memory'] / 1024)) + ' G'
                                request.data['os'] = instance_ip_info['OSName']
                                request.data['sn'] = instance_ip_info['SerialNumber']
                                request.data['disk'] = instance_ip_info['disk_infos']
                                device = []
                                network = {}
                                aliyun_netmask = "255.255.255.0"
                                aliyun_macaddress = instance_ip_info['NetworkInterfaces']["NetworkInterface"][0]['MacAddress']
                                network['ips'] = [{'ip_addr': aliyun_ip, "netmask": aliyun_netmask}]
                                network['mac'] = aliyun_macaddress
                                device.append(network)
                                device[0]['name'] = 'eth0'
                                # print(device)
                                request.data['device'] = device
                                # 不需要自动刷新的数据不要修改，不能动原始数据
                                request.data['remark'] = ins['remark']
                                request.data['created_user'] = ins['created_user']
                                request.data['updated_user'] = ins['updated_user']
                                request.data['server_type'] = ins['device_type']['id']
                                request.data['instance_id'] = ins['instance_id']
                                request.data['idc'] = ins['idc']['id']
                                request.data['service'] = ins['service']['id']
                                request.data['server_purpose'] = ins['server_purpose']['id']
                                request.data['env'] = ins['env']
                                request.data['cabinet'] = ins['cabinet']['id']
                                # 有些数据是一次性数据，无需修改，有就有没有就没有，不管这些数据的更新。比如：
                                # request.data['model_name'] = ins['model_name']['id']
                                # request.data['manufacturer'] = ins['manufacturer']['id']
                                # request.data['cpu_model'] = ins['cpu_model']
                                print(request.data)
                                serializer = self.get_serializer(instance, data=request.data, partial=partial)
                                serializer.is_valid(raise_exception=True)
                                self.perform_update(serializer)
                                if getattr(instance, '_prefetched_objects_cache', None):
                                    # If 'prefetch_related' has been applied to a queryset, we need to
                                    # forcibly invalidate the prefetch cache on the instance.
                                    instance._prefetched_objects_cache = {}

        return response.Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

class flushServerViewset(mixins.UpdateModelMixin,
                         viewsets.GenericViewSet):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        instance_id = request.data['instance_id']
        data = get_aliecs_info(instance_id)
        request.data['disk'] = data['disk_infos']
        all_ecs_infos = data['Instances']['Instance'][0]
        request.data['status'] = all_ecs_infos['Status']
        request.data['cpu_core_count'] = str(all_ecs_infos['Cpu'])+' Core'
        request.data['server_mem'] = str(int(all_ecs_infos['Memory'])/1024)+' G'
        request.data['os'] = all_ecs_infos['OSName']
        # request.data['hostname'] = all_ecs_infos['HostName']
        request.data['sn'] = all_ecs_infos['SerialNumber']
        request.data['cpu_model'] = 'Intel(R) Xeon(R) CPU E5-2682 v4 @ 2.50GHz'
        device = []
        network = {}
        aliyun_ip = all_ecs_infos['NetworkInterfaces']["NetworkInterface"][0]['PrimaryIpAddress']
        aliyun_netmask = "255.255.255.0"
        aliyun_macaddress = all_ecs_infos['NetworkInterfaces']["NetworkInterface"][0]['MacAddress']
        network['ips'] = [{'ip_addr': aliyun_ip, "netmask": aliyun_netmask}]
        network['mac'] = aliyun_macaddress
        device.append(network)
        device[0]['name'] = 'eth0'
        # print(device)
        request.data['device'] = device
        request.data['model_name'] = 4      # Alibaba Cloud ECS
        request.data['idc'] = 2             # 阿里云
        request.data['manufacturer'] = 5    # Alibaba Cloud
        request.data['server_type'] = 0     # 云主机
        print(request.data)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return response.Response(serializer.data)

# 单独对应扩容服务器逻辑的 API （历史原因，最开始某些字段没有做和服务器的关联关系
# 后期由于单独刷一遍数据进入到了数据库，刷入的是名称，所以不能再同步使用服务器的 API，
# 只能是单独的功能使用单独的 API 了，属于无法解决的历史遗留问题....改此代码请慎重..
# 需要与服务器的创建 API 相对应着修改 单独修改影响可能会很大...未来这也是个大坑啊..）
class Server2productViewset(mixins.CreateModelMixin,
                    viewsets.GenericViewSet):

    """
    create:
    扩容服务器
    """
    queryset = Server.objects.all()
    serializer_class = ServerSerializer

    filter_class = ServerFilter
    filter_fields = ('hostname', 'idc', 'cabinet', "service", "server_purpose", "server_type", "remark")

    def create(self, request, *args, **kwargs):
        print(request.data)
        # return
        # 首先判断备注的传值是不是已经存在
        remark = request.data['remark']
        try:
            res = Server.objects.all().filter(remark=remark)
            if res.count() != 0:

                data = {
                    "detail": '备注已经存在',
                }

                return response.Response(data, status=status.HTTP_400_BAD_REQUEST)
            else:
                pass
        except Server.DoesNotExist:
            pass
        # --------扩容云主机-------
        # print(request.data)
        InstanceType = request.data['InstanceType']
        ChargeType = request.data['ChargeType']

        if ChargeType == '按量付费':
            #######################################
            #                                     #
            #  先在阿里云上创建完毕，取出所需字段值     #
            #  写入数据库                           #
            #                                     #
            #######################################
            # 处理 IDC 与 阿里云地域的匹配
            idcid = request.data['idc']
            idcobj = Idc.objects.filter(id__exact=idcid)
            regionId = idcobj.values()[0]['letter']

            # 处理 机柜 与 地域分区的匹配
            cabinetid = request.data['cabinet']
            cabinetobj = Cabinet.objects.filter(id__exact=cabinetid)
            ZoneId = cabinetobj.values()[0]['letter']

            ImageId = request.data['ImageId']

            SecurityGroupIds = []
            for SecurityGroup_Id in request.data['SecurityGroupIds']:
                # SecurityGroup_Id.replace()
                SecurityGroupIds.append(SecurityGroup_Id)

            VSwitchId = request.data['VSwitchId']

            InstanceName = request.data['InstanceName']

            #默认随机主机名
            RandomHostName = ''.join(random.sample(string.ascii_letters, 10))
            Description = RandomHostName
            HostName = RandomHostName

            service_id = request.data['service']
            service_name = Product.objects.get(id=service_id).service_name

            # if 'datadisk' in request.data:
            datadisk = {}
            datadisk['datadisk'] = 200
            ali_create_data = create_ali_ecs_PostPaid(ImageId=ImageId, InstanceType=InstanceType,
                                            SecurityGroupIds=SecurityGroupIds, VSwitchId=VSwitchId,
                                            InstanceName=InstanceName, Description=Description,
                                            HostName=HostName, ZoneId=ZoneId, regionId=regionId,
                                            service_name=service_name, datadisk=datadisk)
            # else:
            #     ali_create_data = create_ali_ecs_PostPaid(ImageId=ImageId, InstanceType=InstanceType,
            #                                     SecurityGroupIds=SecurityGroupIds, VSwitchId=VSwitchId,
            #                                     InstanceName=InstanceName, Description=Description,
            #                                     HostName=HostName, ZoneId=ZoneId, regionId=regionId,
            #                                     service_name=service_name)
            # 通过实例 ID 找到实例 IP 地址，然后传值给 request.data 将整条数据条目写入数据库
            # print(ali_create_data['InstanceIdSets']['InstanceIdSet'])
            instanceID = ali_create_data['InstanceIdSets']['InstanceIdSet'][0]
            # 这里注意一下，不是马上就能拿到 ECS 信息，需要等待一段时间。默认赋值 10 秒。
            import time
            time.sleep(10)

            instanceDescribe = get_aliecs_info(instanceID)
            # print(instanceDescribe)
            all_ecs_infos = instanceDescribe['Instances']['Instance'][0]
            instanceIp = all_ecs_infos['NetworkInterfaces']["NetworkInterface"][0]['PrimaryIpAddress']

            # 更新主机名到阿里云
            server_purpose_id = request.data['server_purpose']
            server_purpose_name = Product.objects.get(id=server_purpose_id).service_name
            # 阿里云主机名不支持有下划线的存在 应用名称中可能有下划线  需要把下划线转为横杠
            Hostname = str(service_name) + '-' + str(server_purpose_name) + '-' + str(instanceIp)+'.ali'
            HostName = Hostname.lower().replace("_", "-")
            # print(HostName)
            ModifyInstance(InstanceId=instanceID, HostName=HostName,
                           InstanceName=InstanceName, Description=InstanceName)
            #将更新后的主机名信息写入资产系统
            request.data['hostname'] = HostName
            request.data['ip'] = instanceIp
            request.data['instance_id'] = instanceID
            # print(SecurityGroupIds)
            request.data['SecurityGroupIds'] = str(SecurityGroupIds)
            # print(instanceIp)
            # print(request.data)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        elif ChargeType == '包年包月':
            #######################################
            #                                     #
            #  先在阿里云上创建完毕，取出所需字段值     #
            #  写入数据库                           #
            #                                     #
            #######################################
            # 处理 IDC 与 阿里云地域的匹配
            idcid = request.data['idc']
            idcobj = Idc.objects.filter(id__exact=idcid)
            regionId = idcobj.values()[0]['letter']
            # print(regionId)
            # print('xxxxxxxx')

            # 处理 机柜 与 地域分区的匹配
            cabinetid = request.data['cabinet']
            cabinetobj = Cabinet.objects.filter(id__exact=cabinetid)
            ZoneId = cabinetobj.values()[0]['letter']

            ImageId = request.data['ImageId']

            SecurityGroupIds = []
            for SecurityGroup_Id in request.data['SecurityGroupIds']:
                # SecurityGroup_Id.replace()
                SecurityGroupIds.append(SecurityGroup_Id)

            VSwitchId = request.data['VSwitchId']

            InstanceName = request.data['InstanceName']

            # 默认随机主机名
            RandomHostName = ''.join(random.sample(string.ascii_letters, 10))
            Description = RandomHostName
            HostName = RandomHostName

            service_id = request.data['service']
            service_name = Product.objects.get(id=service_id).service_name

            PeriodUnit = request.data['PeriodUnit']

            # if 'datadisk' in request.data:
            #     datadisk = request.data['datadisk']
            datadisk = 200
            ali_create_data = create_ali_ecs_PrePaid(ImageId=ImageId, InstanceType=InstanceType,
                                                SecurityGroupIds=SecurityGroupIds, VSwitchId=VSwitchId,
                                                InstanceName=InstanceName, Description=Description,
                                                HostName=HostName, ZoneId=ZoneId, regionId=regionId,
                                                service_name=service_name, datadisk=datadisk, PeriodUnit=PeriodUnit)
            # else:
            #     ali_create_data = create_ali_ecs_PrePaid(ImageId=ImageId, InstanceType=InstanceType,
            #                                         SecurityGroupIds=SecurityGroupIds, VSwitchId=VSwitchId,
            #                                         InstanceName=InstanceName, Description=Description,
            #                                         HostName=HostName, ZoneId=ZoneId, regionId=regionId,
            #                                         service_name=service_name, PeriodUnit=PeriodUnit)
            # 通过实例 ID 找到实例 IP 地址，然后传值给 request.data 将整条数据条目写入数据库
            # print(ali_create_data['InstanceIdSets']['InstanceIdSet'])
            instanceID = ali_create_data['InstanceIdSets']['InstanceIdSet'][0]
            # 这里注意一下，不是马上就能拿到 ECS 信息，需要等待一段时间。默认赋值 10 秒。
            import time
            time.sleep(10)
            instanceDescribe = get_aliecs_info(instanceID)
            # print(instanceDescribe)
            all_ecs_infos = instanceDescribe['Instances']['Instance'][0]
            instanceIp = all_ecs_infos['NetworkInterfaces']["NetworkInterface"][0]['PrimaryIpAddress']

            # 更新主机名到阿里云
            server_purpose_id = request.data['server_purpose']
            server_purpose_name = Product.objects.get(id=server_purpose_id).service_name
            # 阿里云主机名不支持有下划线的存在  应用名称中可能有下划线  需要把下划线转为横杠
            Hostname = str(service_name) + '-' + str(server_purpose_name) + '-' + str(instanceIp) + '.ali'
            HostName = Hostname.lower().replace("_", "-")
            # print(HostName)
            ModifyInstance(InstanceId=instanceID, HostName=HostName,
                           InstanceName=InstanceName, Description=InstanceName)
            # print(instanceID, HostName)
            logger.debug('instanceid: %s; hostname: %s' % (instanceID, HostName))
            # 将更新后的主机名信息写入资产系统
            request.data['hostname'] = HostName
            request.data['ip'] = instanceIp
            request.data['instance_id'] = instanceID
            request.data['SecurityGroupIds'] = str(SecurityGroupIds)

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ServerListViewset(viewsets.ReadOnlyModelViewSet):
    """
    list:
    获取服务器列表

    retrieve:
    获取指定服务器记录
    """
    queryset = Server.objects.all()
    serializer_class = ServerListSerializer
    filter_class = ServerListFilter
    filter_fields = ('hostname', 'idc', "server_purpose", "status")

    def get_queryset(self):
        queryset = super(ServerListViewset, self).get_queryset()
        queryset = queryset.order_by("id")
        return queryset


# class NetwokDeviceViewset(viewsets.ReadOnlyModelViewSet):
class NetwokDeviceViewset(viewsets.ModelViewSet):
    """
    list:
    获取网卡列表

    retrieve:
    获取指定网卡记录

    """
    queryset = NetworkDevice.objects.all()
    serializer_class = NetworkDeviceSerializer
    filter_class = NetworkDeviceFilter
    filter_fields = ("name",)


# class IPViewset(viewsets.ReadOnlyModelViewSet):
class IPViewset(viewsets.ModelViewSet):
    """
    list:
    获取网卡IP列表


    retrieve:
    获取指定网卡IP记录
    """
    queryset = IP.objects.all()
    serializer_class = IPSerializer
    filter_class = IpFilter
    filter_fields = ("ip_addr",)


class ServerAutoReportViewset(mixins.CreateModelMixin,
                          viewsets.GenericViewSet):
    """
    agent采集的信息入库
    """
    queryset = Server.objects.all()
    serializer_class = AutoReportSerializer
    permission_classes = (permissions.AllowAny,)


class ServerCountViewset(viewsets.ViewSet, mixins.ListModelMixin):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Server.objects.all()

    def list(self, request, *args, **kwargs):
        data = self.get_server_nums()
        return response.Response(data)

    def get_server_nums(self):
        ret = {
            "count": self.queryset.count(),
            "ali_host_num": self.queryset.filter(server_type__exact=0).count(),
            "phy_host_num": self.queryset.filter(server_type__exact=1).count(),
            "vm_host_num": self.queryset.filter(server_type__exact=2).count()
        }
        return ret


class VpcViewset(viewsets.ViewSet, mixins.ListModelMixin):
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        data = self.get_vpc()
        return response.Response(data)

    def get_vpc(self):
        #对接 image 数据入库
        image_infos = get_image_infos()

        for image in image_infos:

            imageid = image['imageid']
            imageowner = image['imageowner']
            name = image['name']

            try:
                Images.objects.get(imageid=imageid)
            except Images.DoesNotExist:
                if 'centos' in imageid:
                    Images.objects.create(name=name, imageowner=imageowner, imageid=imageid)
                elif imageowner == 'self':
                    Images.objects.create(name=name, imageowner=imageowner, imageid=imageid)


        #对接实例规格数据入库，分为两部分：包年包月和按量付费
        chargetypes = ['PostPaid', 'PrePaid']

        cores_list = []
        zoneid_list = []
        chargetype_list = []

        for chargetype in chargetypes:
            instype_infos = get_AvailableResource(chargetype)
            # print(instype_infos)
            for instype in instype_infos:
                typename    = instype['typename']
                chargetype  = instype['chargetype']
                cores       = instype['CpuCoreCount']
                mems        = instype['MemorySize']
                chinesename = str(cores)+'Core'+str(int(mems))+'G'+str(typename)
                zone        = instype['zoneid']

                # 判断分区存在与否
                try:
                    zoneid = Cabinet.objects.get(letter=zone).id
                except Cabinet.DoesNotExist:
                    # 写死的地域: 阿里云-华北2-北京
                    idc_id = 2
                    Cabinet.objects.create(name=zone, letter=zone, idc_id=idc_id)
                    zoneid = Cabinet.objects.get(letter=zone).id

                # 判断规格存在与否
                try:
                    AvailableResources.objects.filter(typename=typename).filter(chargetype=chargetype).get(zone_id=zoneid)
                except AvailableResources.DoesNotExist:
                        AvailableResources.objects.create(typename=typename,
                                                          chargetype=chargetype,
                                                          cores=cores, mems=mems,
                                                          chinesename=chinesename,
                                                         zone_id=zoneid)



                # 填充资源匹配关系数据表

                if cores not in cores_list:
                    cores_list.append(cores)
                if chargetype not in chargetype_list:
                    chargetype_list.append(chargetype)
                if zoneid not in zoneid_list:
                    zoneid_list.append(zoneid)

        for core in cores_list:
            for zone_id in zoneid_list:
                for charge_type in chargetype_list:
                    memlist = []
                    res = AvailableResources.objects.filter(cores=core).filter(zone_id=zone_id).filter(chargetype=charge_type)
                    if res.count() != 0:
                        # print(res.all())
                        # print(res.count())
                        for ins in res.all():
                            if ins.mems not in memlist:
                                memlist.append(ins.mems)
                        memlist.sort()
                        # print(memlist)
                        # return
                        try:
                            res_mat = ResourceMatching.objects.filter(chargetype=ins.chargetype).filter(zone_id=zone_id).get(cores=ins.cores)
                        except ResourceMatching.DoesNotExist:
                                ResourceMatching.objects.create(chargetype=ins.chargetype,
                                                              cores=ins.cores, mems=memlist,
                                                              zone_id=ins.zone_id)




        ########################################
        #                                      #
        #  处理 VPC Switch Seg 的关系：获取与更新  #
        #  阿里云与本地数据做匹配                  #
        #  如果阿里云有数据库没有则写入数据库        #
        #  如果阿里云和数据库是一样的数据则直接获取   #
        #                                       #
        #########################################

        vpc_switch_seg_infos = get_vpc_switch_seg_infos()
        vpcnum = 0
        segnum = 0
        switchnum = 0
        for vpc_switch_seg_info in vpc_switch_seg_infos:
            vpcnum += 1
            vpcid = vpc_switch_seg_info["VpcId"]
            vpcname = vpc_switch_seg_info["Vpcname"]
            # 判断 VPC 是否存在
            try:
                vpc_obj = Vpcs.objects.get(vpcid=vpcid)
                # print(vpc_switch_seg_info)
                # print('vpc ok')
            except Vpcs.DoesNotExist:
                Vpcs.objects.create(name=vpcname, vpcid=vpcid)
                vpc_obj = Vpcs.objects.get(vpcid=vpcid)
            # print('判断 VPC 完毕')
            # 判断 seg 是否存在
            for seg in vpc_switch_seg_info["Segs"]:
                # print(seg)
                segnum += 1
                try:
                    SecurityGroups.objects.get(segid=seg['SecurityGroupId'])
                    # print('SecurityGroupId OK')
                except SecurityGroups.DoesNotExist:
                    SecurityGroups.objects.create(name=seg['SecurityGroupName'],
                                                  segid=seg['SecurityGroupId'],
                                                  vpc_id=vpc_obj.id)
                    # print('Create seg OK')
                # print('判断 seg 完毕')
            # print(segnum)
            # 判断 switch 是否存在
            for switch in vpc_switch_seg_info["Switches"]:
                switchnum += 1
                # print(switch)
                try:
                    Switches.objects.get(switchid=switch['VSwitchId'])
                    # print('switch OK')
                except Switches.DoesNotExist:
                    zoneid = switch['ZoneId']
                    # print(zoneid)
                    try:
                        zone_id = Cabinet.objects.get(letter=zoneid).id
                        # print(zone_id)
                        Switches.objects.create(name=switch['VSwitchName'],
                                                switchid=switch['VSwitchId'],
                                                zone_id=zone_id,
                                                vpc_id=vpc_obj.id)
                        # print('Create switch OK')
                    except Cabinet.DoesNotExist:
                        # 写死的地域: 阿里云-华北2-北京
                        idc_id = 2
                        Cabinet.objects.create(name=zoneid, letter=zoneid, idc_id=idc_id)
                        # print('Create zone OK')
                        zone_id = Cabinet.objects.get(letter=zoneid).id
                        # print(zone_id)
                        # print(str(switch['ZoneId'])+str(zoneid)+'   '+str(vpc_obj.id)+'   '+vpc_switch_seg_info["VpcId"]+'  '+switch['VSwitchName']+'  '+switch['VSwitchId'])
                        Switches.objects.create(name=switch['VSwitchName'],
                                                switchid=switch['VSwitchId'],
                                                zone_id=zone_id,
                                                vpc_id=vpc_obj.id)
                #         print('Create switch OK')
                # print('判断 switch 完毕')
        # print('Finish all')

        ret = {
            'VPC': Vpcs.objects.all().count(),
            'Switch': Switches.objects.all().count(),
            'SEG': SecurityGroups.objects.all().count(),
            'Image': Images.objects.all().count(),
            'InsType': AvailableResources.objects.all().count(),
            'ResMatching': ResourceMatching.objects.all().count()
        }

        return ret
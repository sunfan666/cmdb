# -*- coding: UTF-8 -*-
from django.conf import settings

from rest_framework import serializers
from .models import Server, NetworkDevice, IP, Cabinet
from idcs.models import Idc
from cabinet.models import Cabinet
from manufacturers.models import Manufacturer, ProductModel
from raven.contrib.django.raven_compat.models import client

import time
# from .views import TimeStampViewset
fmt = '%Y-%m-%d %a %H:%M:%S'
TimeStamp = time.strftime(fmt, time.localtime(time.time()))

import logging

logger = logging.getLogger(__name__)


class ServerSerializer(serializers.ModelSerializer):
    """
    服务器序列化类
    """
    manufacture_data= serializers.DateField(format="%Y-%m-%d", label="制造日期", required=False, help_text="制造日期")
    warranty_time   = serializers.DateField(format="%Y-%m-%d", label="保修时间", required=False, help_text="保修时间")
    purchasing_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", label="采购时间", required=False, help_text="采购时间")
    updated_time    = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, help_text="更新时间")
    created_time    = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, help_text="创建时间")


    def get_product_name(self, product_obj):
        try:
            return {
                "name": product_obj.service_name,
                "letter": product_obj.module_letter,
                "id": product_obj.id
            }
        except Exception as e:
            return {}

    def get_idc_name(self, idc_obj):
        try:
            return {
                "name": idc_obj.name,
                "letter": idc_obj.letter,
                "id": idc_obj.id
            }
        except Exception as e:
            return {}

    def get_cabinet_name(self, cabinet_obj):
        try:
            return {
                "name": cabinet_obj.name,
                "letter": cabinet_obj.letter,
                "id": cabinet_obj.id
            }
        except Exception as e:
            return {}

    def get_manu(self, manu_obj):
        try:
            return {
                "vendor_name": manu_obj.vendor_name,
                "id": manu_obj.id
            }
        except Exception as e:
            return {}

    def get_pm(self, pm_obj):
        try:
            return {
                "model_name": pm_obj.model_name,
                "id": pm_obj.id
            }
        except Exception as e:
            return {}

    def to_representation(self, instance):

        idc_name = self.get_idc_name(instance.idc)
        cabinet_name = self.get_cabinet_name(instance.cabinet)
        service = self.get_product_name(instance.service)
        server_purpose = self.get_product_name(instance.server_purpose)


        ret = super(ServerSerializer, self).to_representation(instance)

        ret["idc"] = idc_name
        ret["cabinet"] = cabinet_name
        ret["server_purpose"] = server_purpose
        ret["service"] = service
        ret["device_type"] = {
            "id": ret["server_type"],
            "name": self.Meta.vm_status_dict.get(ret["server_type"])
        }
        ret["manufacturer"] = self.get_manu(instance.manufacturer)
        ret["model_name"] = self.get_pm(instance.model_name)
        ret.pop("server_type")
        return ret

    class Meta:
        model = Server
        vm_status_dict = {0: "云主机", 1: "物理机", 2: "虚拟机"}
        fields = '__all__'
        from rest_framework.validators import UniqueValidator
        extra_kwargs = {
            'hostname': {'validators': [UniqueValidator(
                queryset=Server.objects.all(),
                message='主机名重复')]},
            'ip': {'validators': [UniqueValidator(
                queryset=Server.objects.all(),
                message='ip地址重复')]},
            'remark': {'validators': [UniqueValidator(
                queryset=Server.objects.all(),
                message='备注重复')]},
        }


class ServerListSerializer(serializers.ModelSerializer):
    """
    服务器序列化类
    """
    manufacture_data= serializers.DateField(format="%Y-%m-%d", label="制造日期", required=False, help_text="制造日期")
    warranty_time   = serializers.DateField(format="%Y-%m-%d", label="保修时间", required=False, help_text="保修时间")
    purchasing_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", label="采购时间", required=False, help_text="采购时间")
    updated_time      = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True, help_text="检查时间")


    def get_product_name(self, product_obj):
        try:
            return product_obj.module_letter
        except Exception as e:
            return {}

    def get_idc_name(self, idc_obj):
        try:
            return idc_obj.letter
        except Exception as e:
            return {}



    def to_representation(self, instance):
        idc_name = self.get_idc_name(instance.idc)
        service = self.get_product_name(instance.service)
        server_purpose = self.get_product_name(instance.server_purpose)
        ret = super(ServerListSerializer, self).to_representation(instance)
        ip = ret["ip"]
        status = ret["status"]
        env = ret["env"]
        ret = {}
        ret["ip"] = ip
        ret["status"] = status
        ret["env"] = env
        ret["idc"] = idc_name
        ret['service'] = service
        ret["server_purpose"] = server_purpose
        return ret

    class Meta:
        model = Server
        fields = '__all__'

class NetworkDeviceSerializer(serializers.ModelSerializer):
    """
    网卡设备序列化类
    """
    def get_host(self, obj):
        try:
            return {
                "hostname": obj.hostname,
                "id": obj.id
            }
        except Exception as e:
            return {}

    def to_representation(self, instance):
        host = self.get_host(instance.host)
        ret = super(NetworkDeviceSerializer, self).to_representation(instance)
        ret["host"] = host
        return ret

    class Meta:
        model = NetworkDevice
        fields = '__all__'


class IPSerializer(serializers.ModelSerializer):
    """
    IP实例化类
    """
    def get_device(self, obj):
        try:
            return {
                "name": obj.name,
                "id": obj.id
            }
        except Exception as e:
            return {e.args}

    def to_representation(self, instance):
        device = self.get_device(instance.device)
        ret = super(IPSerializer, self).to_representation(instance)
        ret["device"] = device
        return ret

    class Meta:
        model = IP
        fields = '__all__'


class AutoReportSerializer(serializers.Serializer):
    """
    服务器信息自动上报接口序列化类
    """
    hostname        = serializers.CharField(required=True, max_length=50, label="主机名", help_text="主机名")
    os              = serializers.CharField(required=True, max_length=100, label="操作系统", help_text="操作系统")
    manufacturer    = serializers.CharField(required=True, max_length=32, label="厂商名称", help_text="厂商名称")
    model_name      = serializers.CharField(required=True, max_length=32, label="型号", help_text="型号")
    # uuid            = serializers.CharField(required=True, max_length=100, label="UUID", help_text="UUID")
    cpu_core_count  = serializers.CharField(required=True, max_length=100, label="CPU", help_text="CPU")
    server_mem      = serializers.CharField(required=True, max_length=100, label="内存", help_text="内存")
    disk            = serializers.JSONField(required=True, label="磁盘", help_text="磁盘")
    device          = serializers.JSONField(required=True, label="网卡", help_text="网卡")
    sn              = serializers.CharField(required=True, max_length=40, label="SN", help_text="SN")
    ip       = serializers.IPAddressField(required=True, label="IP地址", help_text="IP地址")
    idc             = serializers.CharField(required=True, max_length=30, label="所在机房", help_text="所在机房")
    status          = serializers.CharField(required=False, max_length=32, label="服务器状态", help_text="服务器状态")
    env             = serializers.CharField(required=False, max_length=32, label="服务器状态", help_text="服务器状态")
    server_type     = serializers.IntegerField(required=True, label="机器类型", help_text="机器类型")

    def get_server_obj(self, sn):
        try:
            return Server.objects.get(sn__exact=sn)
        except Server.DoesNotExist:
            return None
        except Server.MultipleObjectsReturned:
            client.captureException()
            raise serializers.ValidationError("存在多条记录")

    def validate_idc(self, idc):
        return self.get_idc_obj(idc)

    def get_idc_obj(self, idc):
        try:
            return Idc.objects.get(name=idc)
        except Idc.DoesNotExist:
            return Idc.objects.create(name=idc)

    def validate_manufacturer(self, manufacturer):
        return self.get_manufacturer_obj(manufacturer)

    def validate(self, attrs):
        attrs["model_name"] = self.get_product_model_obj(attrs["manufacturer"], attrs["model_name"])
        return attrs

    def get_manufacturer_obj(self, manufacturer):
        try:
            return Manufacturer.objects.get(vendor_name=manufacturer)
        except Manufacturer.DoesNotExist:
            return Manufacturer.objects.create(vendor_name=manufacturer)

    def get_product_model_obj(self, manufacturer_obj,  model_name):
        try:
            return manufacturer_obj.productmodel_set.get(model_name__exact=model_name)
        except ProductModel.DoesNotExist:
            return ProductModel.objects.create(model_name=model_name, vendor=manufacturer_obj)

    def create_server(self, validated_data):
        logger.debug("[{}] 新客户端Server记录".format(validated_data["ip"]))
        devices = validated_data.pop("device")
        server_obj = Server.objects.create(**validated_data)

        self.check_server_network_device(server_obj, devices)
        return server_obj

    def check_server_network_device(self, server_obj, devices):
        logger.debug("[{}] 检查服务器的网卡设备".format(server_obj.sn))
        networkDevice_queryset = server_obj.networkdevice_set.all()
        for device in devices:
            print(device)
            if device.get("name", None) and self.filter_network_device(device["name"]):
                try:
                    # update 网卡
                    obj = networkDevice_queryset.get(mac__exact=device.get("mac", ""))
                    obj.name = device['name']
                    obj.mac  = device['mac']
                    # ip
                    self.check_ip(obj, ifnets = device.pop("ips"))
                    obj.save()
                    return obj
                except NetworkDevice.DoesNotExist:
                    # 创建一块网卡记录
                    self.create_network_device(server_obj,device)

    def filter_network_device(self, device_name):
        for filter_name in settings.FILTER_NETWORK_DEVICE:
            if device_name.lower().startswith(filter_name) == True:
                # 需要过滤掉些网卡
                return False
        return True

    def create_network_device(self, server_obj, device):
        ifnets = device.pop("ips")
        device["host"] = server_obj
        network_device_obj = NetworkDevice.objects.create(**device)
        self.check_ip(network_device_obj, ifnets)
        return network_device_obj

    def check_ip(self, network_device_obj, ifnets):
        ip_queryset = network_device_obj.ip_set.all()
        current_ip_objs = []
        for ifnet in ifnets:
            if ifnet.get("ip_addr", None):
                try:
                    # update
                    obj = ip_queryset.get(ip_addr__exact=ifnet["ip_addr"], netmask__exact=ifnet["netmask"])
                    obj.ip_addr = ifnet['ip_addr']
                    obj.netmask = ifnet['netmask']
                    obj.device = network_device_obj
                    obj.save()
                    current_ip_objs.append(obj)
                except IP.DoesNotExist:
                    ip_obj = IP.objects.create(ip_addr=ifnet["ip_addr"], netmask=ifnet["netmask"], device=network_device_obj)
                    current_ip_objs.append(ip_obj)

        not_exists_ip = set(ip_queryset) - set(current_ip_objs)
        for ip_obj in not_exists_ip:
            ip_obj.delete()


    def create(self, validated_data):
        # uuid = validated_data["uuid"].lower()
        # sn   = validated_data["sn"].lower()
        ip = validated_data["ip"]
        logger.debug("同步服务器数据： {}".format(ip))
        try:
            # if sn == uuid or sn.startswith("vmware"):
            #     server_obj = Server.objects.get(uuid__iexact=uuid)
            # else:
            #     server_obj = Server.objects.get(sn__iexact=sn)
            # server_obj = Server.objects.get(sn__iexact=sn)
            server_obj = Server.objects.get(ip__iexact=ip)
        except Server.DoesNotExist:
            return self.create_server(validated_data)
        else:
            return self.update_server(server_obj, validated_data)


    def update_server(self, server_obj, validated_data):
        # 更新
        logger.debug("[{}] 更新客户端Server记录".format(validated_data["ip"]))
        server_obj.hostname = validated_data["hostname"]
        server_obj.os = validated_data["os"]
        server_obj.manufacturer = validated_data["manufacturer"]
        server_obj.model_name = validated_data["model_name"]
        server_obj.cpu_core_count = validated_data["cpu_core_count"]
        server_obj.server_mem = validated_data["server_mem"]
        server_obj.disk = validated_data["disk"]
        server_obj.sn = validated_data["sn"]
        server_obj.idc = validated_data["idc"]
        # server_obj.status = validated_data["status"]
        server_obj.server_type = validated_data["server_type"]
        server_obj.save()
        # update 网卡
        devices = validated_data.pop("device")
        self.check_server_network_device(server_obj, devices)
        return server_obj

    def to_representation(self, instance):
        ret = {
            "hostname": instance.hostname,
            "IP": instance.ip,
            "sn": instance.sn
        }
        return ret


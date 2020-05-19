from rest_framework import mixins, viewsets, permissions, response, status
from .models import Vpcs, SecurityGroups, Switches, Images, AvailableResources, ResourceMatching
from .filter import SwitchFilter, VpcsFilter, SegFilter, ImageFilter, TypeFilter, ResMatchingFilter
from .serializers import VpcSerializer, SecurityGroupsSerializer, SwitchSerializer, ImagesSerializer, \
    TypeSerializer, ResMatchingSerializer

from django.core.exceptions import ValidationError
from django.db.models.query import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import mixins, views
from rest_framework.settings import api_settings


class VpcViewset(viewsets.ModelViewSet):
    """
    retrieve:
    返回指定VPC信息

    list:
    返回VPC列表

    update:
    更新VPC信息

    destroy:
    删除VPC记录

    create:
    创建VPC资源

    partial_update:
    更新部分字段
    """
    queryset = Vpcs.objects.all()
    serializer_class = VpcSerializer
    filter_class = VpcsFilter
    filter_fields = ("name",)

    def destroy(self, request, *args, **kwargs):
        ret = {"status": 0}
        instance = self.get_object()

        if Switches.objects.filter(vpc_id__exact=instance.id).count() != 0:
            ret["status"] = 1
            ret["errmsg"] = "该VPC下边还有Switch记录，不能删除!!!!"
            if SecurityGroups.objects.filter(vpc_id__exact=instance.id).count() != 0:
                ret["status"] = 2
                ret["errmsg"] = "该VPC下边还有SecurityGroup记录，不能删除!!!!"
            return response.Response(ret, status=status.HTTP_200_OK)

        self.perform_destroy(instance)
        return response.Response(ret, status=status.HTTP_200_OK)

class SwitchViewset(viewsets.ModelViewSet):
    """
    retrieve:
    返回指定Switch信息

    list:
    返回Switch列表

    update:
    更新Switch信息

    destroy:
    删除Switch记录

    create:
    创建Switch资源

    partial_update:
    更新部分字段
    """
    queryset = Switches.objects.all()
    serializer_class = SwitchSerializer
    filter_class = SwitchFilter
    filter_fields = ("name",)

class SecurityGroupsViewset(viewsets.ModelViewSet):
    """
    retrieve:
    返回指定SecurityGroup信息

    list:
    返回SecurityGroup列表

    update:
    更新SecurityGroup信息

    destroy:
    删除SecurityGroup记录

    create:
    创建SecurityGroup资源

    partial_update:
    更新部分字段
    """
    queryset = SecurityGroups.objects.all()
    serializer_class = SecurityGroupsSerializer
    filter_class = SegFilter
    filter_fields = ("name",)

class ImagesViewset(viewsets.ModelViewSet):
    """
    retrieve:
    返回指定Image信息

    list:
    返回Image列表

    update:
    更新Image信息

    destroy:
    删除Image记录

    create:
    创建Image资源

    partial_update:
    更新部分字段
    """
    queryset = Images.objects.all()
    serializer_class = ImagesSerializer
    filter_class = ImageFilter
    filter_fields = ("name",)

class InstanceTypeViewset(viewsets.ModelViewSet):
    """
    retrieve:
    返回指定InstanceType信息

    list:
    返回InstanceType列表

    update:
    更新InstanceType信息

    destroy:
    删除InstanceType记录

    create:
    创建InstanceType资源

    partial_update:
    更新部分字段
    """
    queryset = AvailableResources.objects.all()
    serializer_class = TypeSerializer
    filter_class = TypeFilter
    filter_fields = ("typename", "chargetype", "chinesename", "zone")

class ResourceMatchingViewset(viewsets.ModelViewSet):
    """
    retrieve:
    返回指定ResourceMatching信息

    list:
    返回ResourceMatching列表

    update:
    更新ResourceMatching信息

    destroy:
    删除ResourceMatching记录

    create:
    创建ResourceMatching资源

    partial_update:
    更新部分字段
    """
    queryset = ResourceMatching.objects.all()
    serializer_class = ResMatchingSerializer
    filter_class = ResMatchingFilter
    filter_fields = ("chargetype", "chinesename", "zone")
import django_filters

from .models import Vpcs, Switches, SecurityGroups, Images, AvailableResources, ResourceMatching


class VpcsFilter(django_filters.rest_framework.FilterSet):
    """
    VPC过滤类
    """
    name = django_filters.CharFilter(name="name", lookup_expr="icontains")


    class Meta:
        model  = Vpcs
        fields = ['name', 'vpcid']

class SwitchFilter(django_filters.rest_framework.FilterSet):
    """
    Switch过滤类
    """
    name = django_filters.CharFilter(name="name", lookup_expr="icontains")

    class Meta:
        model  = Switches
        fields = ['name', 'switchid', 'vpc', 'zone']


class SegFilter(django_filters.rest_framework.FilterSet):
    """
    SecurityGroup过滤类
    """
    name = django_filters.CharFilter(name="name", lookup_expr="icontains")


    class Meta:
        model  = SecurityGroups
        fields = ['name', 'segid', 'vpc']

class ImageFilter(django_filters.rest_framework.FilterSet):
    """
    Image过滤类
    """
    name = django_filters.CharFilter(name="name", lookup_expr="icontains")


    class Meta:
        model  = Images
        fields = ['name', 'imageid', 'imageowner']

class TypeFilter(django_filters.rest_framework.FilterSet):
    """
    InstacneType过滤类
    """
    typename = django_filters.CharFilter(name="typename", lookup_expr="icontains")

    class Meta:
        model  = AvailableResources
        fields = ['typename', 'chinesename', 'chargetype', 'cores', 'mems', 'zone']

class ResMatchingFilter(django_filters.rest_framework.FilterSet):
    """
    ResMatching过滤类
    """
    chargetype = django_filters.CharFilter(name="chargetype", lookup_expr="icontains")

    class Meta:
        model  = ResourceMatching
        fields = ['chargetype', 'cores', 'zone']



import django_filters
from django.db.models import Q

from .models import Server, NetworkDevice, IP
from products.models import Product
from idcs.models import Idc

class ServerListFilter(django_filters.rest_framework.FilterSet):
    """
    服务器过滤类
    """

    status          = django_filters.CharFilter(method='search_status')
    hostname        = django_filters.CharFilter(method='search_server')
    idc             = django_filters.NumberFilter(method="search_idc")
    cabinet         = django_filters.NumberFilter(method="search_cabinet")
    service         = django_filters.NumberFilter(method="search_first_product")
    server_purpose  = django_filters.CharFilter(method="search_second_product")
    server_type     = django_filters.ChoiceFilter(name="server_type", choices=((0,"aliyun"), (1, "物理机"),(2, "虚拟机")), lookup_expr="exact")


    def search_server_type(self,queryset, name, value):
        if value == 0:
            return queryset.filter(server_type__in=[0, 1])
        else:
            return queryset.filter(server_type=value)


    def search_second_product(self, queryset, name, value):
        # print('value is %s' % value)
        # print(name)
        # print(queryset)
        # if value > 0:
        #     data = queryset.filter(server_purpose_id__exact=value)
        #     print(data)
        #     return queryset.filter(server_purpose_id__exact=value)
        # elif value == -1:
        #     return queryset.filter(server_purpose_id__isnull=True)
        # else:
        #     return queryset
        # return queryset.filter(server_purpose=value)
        productId = 0
        # print(productId)
        try:
            obj = Product.objects.get(module_letter__exact=value)
            productId = obj.id
            # print(productId)
        except:
            pass
        # print(productId)
        return queryset.filter(server_purpose_id__exact=productId)

    def search_idc(self, queryset, name, value):
        if value > 0:
            return queryset.filter(idc_id__exact=value)
        elif value == -1:
            return queryset.filter(idc_id__isnull=True)
        else:
            return queryset

    def search_first_product(self, queryset, name, value):
        if value > 0:
            return queryset.filter(service_id__exact=value)
        elif value == -1:
            return queryset.filter(service_id__isnull=True)
        else:
            return queryset

    def search_server(self, queryset, name, value):
        return queryset.filter(Q(hostname__icontains=value)|Q(ip__icontains=value))

    def search_status(self, queryset, name, value):
        return queryset.filter(Q(status__icontains=value))


    def search_cabinet(self, queryset, name, value):
        if value > 0:
            return queryset.filter(cabinet_id__exact=value)
        elif value == -1:
            return queryset.filter(cabinet_id__isnull=True)
        else:
            return queryset

    class Meta:
        model = Server
        fields = ['hostname', 'idc', 'cabinet', "service_id", "server_purpose", "server_type"]


# class NetworkDeviceFilter(django_filters.rest_framework.FilterSet):
#     """
#     网卡过滤类
#     """
#     name = django_filters.CharFilter(method='search_name')
#
#     def search_name(self, queryset, name, value):
#         return queryset.filter(Q(name__icontains=value))
#
#
#     class Meta:
#         model  = NetworkDevice
#         fields = ['name']
#
#
# class IpFilter(django_filters.rest_framework.FilterSet):
#     """
#     IP过滤类
#     """
#     ip_addr = django_filters.CharFilter(method='search_ip')
#
#     def search_ip(self, queryset, ip_addr, value):
#         return queryset.filter(Q(ip_addr__icontains=value))
#
#
#     class Meta:
#         model  = IP
#         fields = ['ip_addr']
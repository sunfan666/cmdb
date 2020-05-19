import django_filters
from django.db.models import Q

from .models import Server
from products.models import Product
from idcs.models import Idc

# from django.shortcuts import get_object_or_404

class ServerListFilter(django_filters.rest_framework.FilterSet):
    """
    服务器过滤类
    """

    status          = django_filters.CharFilter(method='search_status')
    hostname        = django_filters.CharFilter(method='search_server')
    idc             = django_filters.CharFilter(method="search_idc")
    service         = django_filters.CharFilter(method="search_first_product")
    server_purpose  = django_filters.CharFilter(method="search_second_product")



    def search_first_product(self, queryset, name, value):
        # try:
        #     obj = Product.objects.get(module_letter__exact=value)
        #     print(type(value))
        #     # if obj 判断是传入的 ID 还是 name
        # except Product.DoesNotExist:
        #     print('不存在该业务线')
        try:
            value = int(value)
            print(value)
            print(type(value))
            if value > 0:
                print('OK')
                # data = queryset.filter(server_purpose_id__exact=value)
                # print(data)
                return queryset.filter(service_id__exact=value)
            elif value == -1:
                return queryset.filter(service_id__isnull=True)
            else:
                return queryset
            return queryset.filter(service=value)
        except ValueError:
            productId = 0
            print(productId)
            print(value)
            try:
                obj = Product.objects.get(service_name__exact=value)
                print(obj)
                productId = obj.id
            except:
                pass
            return queryset.filter(service_id__exact=productId)



        # obj = get_object_or_404(Product, module_letter__exact=value)
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

        # if isinstance(value, int) is True:
        # if type(value) is str:

        # productId = 0
        # try:
        #     obj = Product.objects.get(module_letter__exact=value)
        #     productId = obj.id
        # except:
        #     pass
        # # print(productId)
        # return queryset.filter(service_id__exact=productId)

    def search_second_product(self, queryset, name, value):
        print('value is %s' % value)
        print(name)
        try:
            value = int(value)
            print(value)
            print(type(value))
            if value > 0:
                print('OK')
                # data = queryset.filter(server_purpose_id__exact=value)
                # print(data)
                return queryset.filter(server_purpose_id__exact=value)
            elif value == -1:
                return queryset.filter(server_purpose_id__isnull=True)
            else:
                return queryset
            return queryset.filter(server_purpose=value)
        except ValueError:
            productId = 0
            print(productId)
            print(value)
            try:
                obj = Product.objects.get(service_name__exact=value)
                productId = obj.id
            except:
                pass
            return queryset.filter(server_purpose_id__exact=productId)
        # # print(queryset)
        # # if value > 0:
        # #     data = queryset.filter(server_purpose_id__exact=value)
        # #     print(data)
        # #     return queryset.filter(server_purpose_id__exact=value)
        # # elif value == -1:
        # #     return queryset.filter(server_purpose_id__isnull=True)
        # # else:
        # #     return queryset
        # # return queryset.filter(server_purpose=value)
        # productId = 0
        # try:
        #     obj = Product.objects.get(module_letter__exact=value)
        #     productId = obj.id
        # except:
        #     pass
        # # print(productId)
        # return queryset.filter(server_purpose_id__exact=productId)

    def search_idc(self, queryset, name, value):
        # if value > 0:
        #     return queryset.filter(idc_id__exact=value)
        # elif value == -1:
        #     return queryset.filter(idc_id__isnull=True)
        # else:
        #     return queryset
        idcid = 0
        try:
            obj =  Idc.objects.get(letter__exact=value)
            idcid = obj.id
        except:
            pass
        return queryset.filter(idc_id__exact=idcid)

    def search_server(self, queryset, name, value):
        return queryset.filter(Q(hostname__icontains=value)|Q(ip__icontains=value))

    def search_status(self, queryset, name, value):
        return queryset.filter(Q(status__icontains=value))



    class Meta:
        model = Server
        fields = ['hostname', 'idc',  "service", "server_purpose", "status"]

# import django_filters
# from django.db.models import Q
#
# from .models import Server
# from products.models import Product
# from idcs.models import Idc
#
# class ServerListFilter(django_filters.rest_framework.FilterSet):
#     """
#     服务器过滤类
#     """
#
#     status          = django_filters.CharFilter(method='search_status')
#     hostname        = django_filters.CharFilter(method='search_server')
#     idc             = django_filters.CharFilter(method="search_idc")
#     service         = django_filters.CharFilter(method="search_first_product")
#     server_purpose  = django_filters.CharFilter(method="search_second_product")
#
#
#     # def search_first_product(self, queryset, name, value):
#     #     # print('value is %s' % value)
#     #     # print(name)
#     #     # print(queryset)
#     #     # if value > 0:
#     #     #     data = queryset.filter(server_purpose_id__exact=value)
#     #     #     print(data)
#     #     #     return queryset.filter(server_purpose_id__exact=value)
#     #     # elif value == -1:
#     #     #     return queryset.filter(server_purpose_id__isnull=True)
#     #     # else:
#     #     #     return queryset
#     #     # return queryset.filter(server_purpose=value)
#     #     productId = 0
#     #     try:
#     #         obj = Product.objects.get(module_letter__exact=value)
#     #         productId = obj.id
#     #     except:
#     #         pass
#     #     # print(productId)
#     #     return queryset.filter(service_id__exact=productId)
#     #
#     # def search_second_product(self, queryset, name, value):
#     #     # print('value is %s' % value)
#     #     # print(name)
#     #     # print(queryset)
#     #     # if value > 0:
#     #     #     data = queryset.filter(server_purpose_id__exact=value)
#     #     #     print(data)
#     #     #     return queryset.filter(server_purpose_id__exact=value)
#     #     # elif value == -1:
#     #     #     return queryset.filter(server_purpose_id__isnull=True)
#     #     # else:
#     #     #     return queryset
#     #     # return queryset.filter(server_purpose=value)
#     #     productId = 0
#     #     try:
#     #         obj = Product.objects.get(module_letter__exact=value)
#     #         productId = obj.id
#     #     except:
#     #         pass
#     #     # print(productId)
#     #     return queryset.filter(server_purpose_id__exact=productId)
#
#     def search_first_product(self, queryset, name, value):
#         try:
#             value = int(value)
#             print(value)
#             print(type(value))
#             if value > 0:
#                 return queryset.filter(service_id__exact=value)
#             elif value == -1:
#                 return queryset.filter(service_id__isnull=True)
#             else:
#                 return queryset
#             return queryset.filter(service=value)
#         except ValueError:
#             productId = 0
#             print(productId)
#             print(value)
#             try:
#                 # obj = Product.objects.get(module_letter__exact=value)
#                 obj = Product.objects.get(service_name__exact=value)
#                 productId = obj.id
#             except:
#                 pass
#             return queryset.filter(service_id__exact=productId)
#
#
#
#         # obj = get_object_or_404(Product, module_letter__exact=value)
#         # print('value is %s' % value)
#         # print(name)
#         # print(queryset)
#         # if value > 0:
#         #     data = queryset.filter(server_purpose_id__exact=value)
#         #     print(data)
#         #     return queryset.filter(server_purpose_id__exact=value)
#         # elif value == -1:
#         #     return queryset.filter(server_purpose_id__isnull=True)
#         # else:
#         #     return queryset
#         # return queryset.filter(server_purpose=value)
#
#         # if isinstance(value, int) is True:
#         # if type(value) is str:
#
#         # productId = 0
#         # try:
#         #     obj = Product.objects.get(module_letter__exact=value)
#         #     productId = obj.id
#         # except:
#         #     pass
#         # # print(productId)
#         # return queryset.filter(service_id__exact=productId)
#
#     def search_second_product(self, queryset, name, value):
#         try:
#             value = int(value)
#             print(value)
#             print(type(value))
#             if value > 0:
#                 return queryset.filter(server_purpose_id__exact=value)
#             elif value == -1:
#                 return queryset.filter(server_purpose_id__isnull=True)
#             else:
#                 return queryset
#             return queryset.filter(server_purpose=value)
#         except ValueError:
#             productId = 0
#             print(productId)
#             print(value)
#             try:
#                 obj = Product.objects.get(service_name__exact=value)
#                 productId = obj.id
#             except:
#                 pass
#             return queryset.filter(server_purpose_id__exact=productId)
#         # # print(queryset)
#         # # if value > 0:
#         # #     data = queryset.filter(server_purpose_id__exact=value)
#         # #     print(data)
#         # #     return queryset.filter(server_purpose_id__exact=value)
#         # # elif value == -1:
#         # #     return queryset.filter(server_purpose_id__isnull=True)
#         # # else:
#         # #     return queryset
#         # # return queryset.filter(server_purpose=value)
#         # productId = 0
#         # try:
#         #     obj = Product.objects.get(module_letter__exact=value)
#         #     productId = obj.id
#         # except:
#         #     pass
#         # # print(productId)
#         # return queryset.filter(server_purpose_id__exact=productId)
#
#     def search_idc(self, queryset, name, value):
#         # if value > 0:
#         #     return queryset.filter(idc_id__exact=value)
#         # elif value == -1:
#         #     return queryset.filter(idc_id__isnull=True)
#         # else:
#         #     return queryset
#         idcid = 0
#         try:
#             obj =  Idc.objects.get(letter__exact=value)
#             idcid = obj.id
#         except:
#             pass
#         return queryset.filter(idc_id__exact=idcid)
#
#     def search_server(self, queryset, name, value):
#         return queryset.filter(Q(hostname__icontains=value)|Q(ip__icontains=value))
#
#     def search_status(self, queryset, name, value):
#         return queryset.filter(Q(status__icontains=value))
#
#
#
#     class Meta:
#         model = Server
#         fields = ['hostname', 'idc',  "service", "server_purpose", "status"]
#
#
# # class NetworkDeviceFilter(django_filters.rest_framework.FilterSet):
# #     """
# #     网卡过滤类
# #     """
# #     name = django_filters.CharFilter(method='search_name')
# #
# #     def search_name(self, queryset, name, value):
# #         return queryset.filter(Q(name__icontains=value))
# #
# #
# #     class Meta:
# #         model  = NetworkDevice
# #         fields = ['name']
# #
# #
# # class IpFilter(django_filters.rest_framework.FilterSet):
# #     """
# #     网卡过滤类
# #     """
# #     ip_addr = django_filters.CharFilter(method='search_ip')
# #
# #     def search_ip(self, queryset, ip_addr, value):
# #         return queryset.filter(Q(ip_addr__icontains=value))
# #
# #
# #     class Meta:
# #         model  = IP
# #         fields = ['ip_addr']

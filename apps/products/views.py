from rest_framework import mixins, viewsets, response, status
from .models import Product
from .serializers import ProductSerializer, ProductssSerializer
from .filters import ProductFilter
from servers.models import Server
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.models import Group
from users.views import UserInfoViewset
from .common import get_product_tree
from rest_framework.generics import get_object_or_404


#专门为前端界面‘业务线管理’提供接口
class ProductViewset(viewsets.ModelViewSet):
    """
    retrieve:
    返回指定业务线信息

    list:
    返回业务线列表

    update:
    更新业务线信息

    destroy:
    删除业务线记录

    create:
    创建业务线资源

    partial_update:
    更新部分字段
    """
    queryset = Product.objects.all()
    serializer_class = ProductssSerializer
    extra_perms_map = {
        "GET": ["products.view_product"]
    }
    filter_class = ProductFilter
    filter_fields = ("pid",)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        print(serializer.data["id"])
        opuser = User.objects.get(username=serializer.data["op_interface"][0]['username'])
        rduser = User.objects.get(username=serializer.data["dev_interface"][0]['username'])
        opgroup = opuser.groups.first()
        rdgroup = rduser.groups.first()

        opgroup.product_set.add(serializer.data["id"])
        rdgroup.product_set.add(serializer.data["id"])

        return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        # partial = kwargs.pop('partial', False)
        instance = self.get_object()
        # print(request.data)
        serializer = self.get_serializer(instance, data=request.data,)
        # print(serializer)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return response.Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        ret = {"status": 0}
        instance = self.get_object()
        if instance.pid == 0:
            # 顶级业务线
            # 查找二级业务线
            if Product.objects.filter(pid__exact=instance.id).count() != 0:
                ret["status"] = 1
                ret["errmsg"] = "该业务线下还有产品线"
                return response.Response(ret, status=status.HTTP_400_BAD_REQUEST)
        else:
            # 二级业务线
            if Server.objects.filter(server_purpose__id__exact=instance.id).count() != 0:
                ret["status"] = 1
                ret["errmsg"] = "该分组下还有资产，不能删除"
                return response.Response(ret, status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(instance)
        return response.Response(ret, status=status.HTTP_204_NO_CONTENT)

#专门为前端界面‘服务器’提供接口
class ProductsViewset(viewsets.ModelViewSet):
    """
    retrieve:
    返回指定业务线信息

    list:
    返回业务线列表

    update:
    更新业务线信息

    destroy:
    删除业务线记录

    create:
    创建业务线资源

    partial_update:
    更新部分字段
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    extra_perms_map = {
        "GET": ["products.view_product"]
    }
    filter_class = ProductFilter
    filter_fields = ("pid",)


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        print(serializer.data["id"])
        opuser = User.objects.get(username=serializer.data["op_interface"][0]['username'])
        rduser = User.objects.get(username=serializer.data["dev_interface"][0]['username'])
        opgroup = opuser.groups.first()
        rdgroup = rduser.groups.first()

        opgroup.product_set.add(serializer.data["id"])
        rdgroup.product_set.add(serializer.data["id"])

        return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        # partial = kwargs.pop('partial', False)
        instance = self.get_object()
        # print(request.data)
        serializer = self.get_serializer(instance, data=request.data,)
        # print(serializer)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return response.Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        ret = {"status": 0}
        instance = self.get_object()
        if instance.pid == 0:
            # 顶级业务线
            # 查找二级业务线
            if Product.objects.filter(pid__exact=instance.id).count() != 0:
                ret["status"] = 1
                ret["errmsg"] = "该业务线下还有产品线"
                return response.Response(ret, status=status.HTTP_400_BAD_REQUEST)
        else:
            # 二级业务线
            if Server.objects.filter(server_purpose__id__exact=instance.id).count() != 0:
                ret["status"] = 1
                ret["errmsg"] = "该分组下还有资产，不能删除"
                return response.Response(ret, status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(instance)
        return response.Response(ret, status=status.HTTP_204_NO_CONTENT)


class ProductManageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    list:
    业务线列表
    """
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    def list(self, request, *args, **kwargs):
        data = self.get_products()
        return response.Response(data)

    def get_products(self):
        ret = []
        for obj in self.queryset.filter(pid=0):
            node = self.get_node(obj)
            node["children"] = self.get_children(obj.id)
            ret.append(node)
        return ret

    def get_children(self, pid):
        ret = []
        for obj in self.queryset.filter(pid=pid):
            node = self.get_node(obj)
            node["children"] = self.get_children(obj.id)
            if node["children"] == []:
                # ret.append(self.get_node(obj))
                ret.append(self.get_node(obj))
            else:
                ret.append(node)
            # ret.append(self.get_node(obj))
        return ret

    def get_node(self, product_obj):
        node = {}
        node["id"] = product_obj.id
        node["label"] = product_obj.service_name
        node["pid"] = product_obj.pid
        return node


class GroupProductViewset(mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
# class GroupProductViewset(viewsets.ModelViewSet):
    """
    用户组节点

    retrieve:
    返回指定用户组的节点列表

    update:
    给指定用户组增加节点，参数nid: node id

    destroy:
    删除指定组下的节点，参数nid: node id
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # def list(self, request, *args, **kwargs):
    #     data = self.get_products()
    #     return response.Response(data)
    #
    # def get_products(self):
    #     ret = []
    #     for obj in self.queryset.filter(pid=0):
    #         node = self.get_node(obj)
    #         node["children"] = self.get_children(obj.id)
    #         ret.append(node)
    #     return ret
    #
    # def get_children(self, pid):
    #     ret = []
    #     for obj in self.queryset.filter(pid=pid):
    #         ret.append(self.get_node(obj))
    #     return ret
    #
    # def get_node(self, product_obj):
    #     node = {}
    #     node["id"] = product_obj.id
    #     node["label"] = product_obj.service_name
    #     node["pid"] = product_obj.pid
    #     return node

    def process_products(self, group_permission_queryset, data):
        for record in data:
            try:
                group_permission_queryset.get(pk=record.get("id", None))
                record["status"] = True
            except:
                pass
        return data

    def get_group_products(self):
        groupobj = self.get_object()
        queryset = groupobj.product_set.all()
        data = get_product_tree(queryset)
        return response.Response(data)

    def get_modify_products(self):
        groupobj = self.get_object()
        group_product_queryset = groupobj.product_set.all()
        queryset = Product.objects.all()
        ret = {}
        ret["data"] = get_product_tree(queryset, group_product_queryset)
        ret["permissions"] = [obj.id for obj in group_product_queryset]
        return response.Response(ret)

    def retrieve(self, request, *args, **kwargs):
        modify = request.GET.get("modify", None)
        if modify is not None:
            return self.get_modify_products()
        else:
            return self.get_group_products()

    def get_object(self):
        queryset = Group.objects.all()
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        self.check_object_permissions(self.request, obj)
        return obj

    def update(self, request, *args, **kwargs):
        groupobj = self.get_object()
        product_objects = Product.objects.filter(pk__in=request.data.get("nid"))
        groupobj.product_set = product_objects
        # if product_objects:
        ret = {"status": 0}
        # else:
        #     ret = {"errmsg": "传值错误请检查"}
        return response.Response(ret, status=status.HTTP_200_OK)
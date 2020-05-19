from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Product
from .common2 import get_product_tree

User = get_user_model()

# global querysets
# querysets = ''

class ProductSerializer(serializers.ModelSerializer):
    def validate_pid(self, pid):
        if pid > 0:
            try:
                product_obj = Product.objects.get(pk=pid)
                # print(product_obj)
                # print(pid)
                # if product_obj.pid != 0:
                #     return serializers.ValidationError("上级业务线错误")
            except Product.DoesNotExist:
                return serializers.ValidationError("上级业务线不存在")
            return pid
        else:
            # return 0
            return pid


    def get_user_response(self, user_queryset):
        ret = []
        for user in user_queryset:
            ret.append({
                "username": user.username,
                "name": user.name,
                "email": user.email,
                "id": user.id,
            })
        return ret

    def get_group_response(self, group_queryset):
        ret = []
        for group in group_queryset:
            ret.append({
                "name": group.name,
                "id": group.id,
            })
        return ret



    def to_representation(self, instance):
        queryset = Product.objects.filter(id__exact=instance.id)
        # print(queryset)
        if instance.pid == 0:
            dev_interface = self.get_user_response(instance.dev_interface.all())
            op_interface = self.get_user_response(instance.op_interface.all())
            groups = self.get_group_response(instance.groups.all())
            res = super(ProductSerializer, self).to_representation(instance)

            res["dev_interface"] = dev_interface
            res["op_interface"] = op_interface
            res["groups"] = groups
            return res


        else:
            data = get_product_tree(queryset)

            # ret = []
            #
            # ret = data[0]
            print(len(data))
            ret = []
            for res in data:
                dev_interface = self.get_user_response(instance.dev_interface.all())
                op_interface = self.get_user_response(instance.op_interface.all())
                groups = self.get_group_response(instance.groups.all())
                # ret = super(ProductSerializer, self).to_representation(instance)
                res["dev_interface"] = dev_interface
                res["op_interface"] = op_interface
                res["groups"] = groups
                print(res)
                ret.append(res)

            return ret


    def update(self, instance, validated_data):
        instance.service_name = validated_data.get("service_name", instance.service_name)
        instance.module_letter = validated_data.get("module_letter", instance.module_letter)
        instance.pid = validated_data.get("pid", instance.pid)
        instance.dev_interface = validated_data.get("dev_interface", instance.dev_interface)
        instance.op_interface = validated_data.get("op_interface", instance.op_interface)
        instance.save()
        return instance

    class Meta:
        model = Product
        fields = '__all__'


class ProductssSerializer(serializers.ModelSerializer):
    def validate_pid(self, pid):
        if pid > 0:
            try:
                Product.objects.get(pk=pid)
            except Product.DoesNotExist:
                return serializers.ValidationError("上级业务线不存在")
            return pid
        else:
            return pid


    def get_user_response(self, user_queryset):
        ret = []
        for user in user_queryset:
            ret.append({
                "username": user.username,
                "name": user.name,
                "email": user.email,
                "id": user.id,
            })
        return ret

    def get_group_response(self, group_queryset):
        ret = []
        for group in group_queryset:
            ret.append({
                "name": group.name,
                "id": group.id,
            })
        return ret



    def to_representation(self, instance):
        dev_interface = self.get_user_response(instance.dev_interface.all())
        op_interface = self.get_user_response(instance.op_interface.all())
        groups = self.get_group_response(instance.groups.all())
        ret = super(ProductssSerializer, self).to_representation(instance)

        ret["dev_interface"] = dev_interface
        ret["op_interface"] = op_interface
        ret["groups"] = groups
        #返回上级业务线名称，而不仅仅是 pid
        if ret["pid"] != 0:
            _pser_name = Product.objects.get(id=ret["pid"])
            ret["pser_name"] = _pser_name.service_name
        return ret


    def update(self, instance, validated_data):
        instance.service_name = validated_data.get("service_name", instance.service_name)
        instance.module_letter = validated_data.get("module_letter", instance.module_letter)
        instance.pid = validated_data.get("pid", instance.pid)
        instance.dev_interface = validated_data.get("dev_interface", instance.dev_interface)
        instance.op_interface = validated_data.get("op_interface", instance.op_interface)
        instance.save()
        return instance

    class Meta:
        model = Product
        fields = '__all__'



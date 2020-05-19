from rest_framework import serializers

from rest_framework.validators import UniqueValidator

from .models import Vpcs, SecurityGroups, Switches, Images, AvailableResources, ResourceMatching

from cabinet.models import Cabinet


class VpcSerializer(serializers.ModelSerializer):
    """
    VPC序列化类
    """
    class Meta:
        model = Vpcs
        fields = '__all__'
        extra_kwargs = {
            'name': {'validators': [UniqueValidator(
                queryset=Vpcs.objects.all(),
                message='Switch 名称重复')]},
            'vpcid': {'validators': [UniqueValidator(
                queryset=Vpcs.objects.all(),
                message='VPCid 重复')]},
        }

class SwitchSerializer(serializers.ModelSerializer):
    """
    Switch序列化类
    """

    def get_zone_name(self, zone_id):
        try:
            return {
                "name": Cabinet.objects.get(id=zone_id).name,
                "id": zone_id
            }
        except Exception as e:
            return {}


    def get_vpc_name(self, vpc_id):
        try:
            return {
                "name": Vpcs.objects.get(id=vpc_id).name,
                "vpcid": Vpcs.objects.get(id=vpc_id).vpcid,
                "id": vpc_id
            }
        except Exception as e:
            return {}

    def to_representation(self, instance):
        zone_name = self.get_zone_name(instance.zone_id)
        vpc_name = self.get_vpc_name(instance.vpc_id)

        ret = super(SwitchSerializer, self).to_representation(instance)

        ret['zone'] = zone_name
        ret['vpc'] = vpc_name

        return ret

    class Meta:
        model = Switches
        fields = '__all__'
        extra_kwargs = {
            'name': {'validators': [UniqueValidator(
                queryset=Switches.objects.all(),
                message='Switch 名称重复')]},
            'switchid': {'validators': [UniqueValidator(
                queryset=Switches.objects.all(),
                message='Switch ID重复')]},
        }

class SecurityGroupsSerializer(serializers.ModelSerializer):
    """
    SecurityGroups序列化类
    """

    def get_vpc_name(self, vpc_id):
        try:
            return {
                "name": Vpcs.objects.get(id=vpc_id).name,
                "vpcid": Vpcs.objects.get(id=vpc_id).vpcid,
                "id": vpc_id
            }
        except Exception as e:
            return {}

    def to_representation(self, instance):
        vpc_name = self.get_vpc_name(instance.vpc_id)

        ret = super(SecurityGroupsSerializer, self).to_representation(instance)

        ret['vpc'] = vpc_name

        return ret


    class Meta:
        model = SecurityGroups
        fields = '__all__'
        extra_kwargs = {
            'name': {'validators': [UniqueValidator(
                queryset=SecurityGroups.objects.all(),
                message='安全组名称重复')]},
            'segid': {'validators': [UniqueValidator(
                queryset=SecurityGroups.objects.all(),
                message='安全组ID重复')]},
        }

class ImagesSerializer(serializers.ModelSerializer):
    """
    Images序列化类
    """

    class Meta:
        model = Images
        fields = '__all__'
        extra_kwargs = {
            'name': {'validators': [UniqueValidator(
                queryset=Images.objects.all(),
                message='镜像名称重复')]},
            'imageid': {'validators': [UniqueValidator(
                queryset=Images.objects.all(),
                message='镜像ID重复')]},
        }

class TypeSerializer(serializers.ModelSerializer):
    """
    Type序列化类
    """

    class Meta:
        model = AvailableResources
        fields = '__all__'
        extra_kwargs = {
            'typename': {'validators': [UniqueValidator(
                queryset=AvailableResources.objects.all(),
                message='规格名称重复')]}
        }

class ResMatchingSerializer(serializers.ModelSerializer):
    """
    ResMatching序列化类
    """

    class Meta:
        model = ResourceMatching
        fields = '__all__'
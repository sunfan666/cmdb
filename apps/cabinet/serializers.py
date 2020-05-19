
from .models import Cabinet
from rest_framework import serializers

class CabinetSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        idc_obj = instance.idc
        ret = super(CabinetSerializer, self).to_representation(instance)
        ret["idc"] = {
                "name": idc_obj.name,
                "id": idc_obj.id
            }
        return ret

    class Meta:
        model = Cabinet
        fields = '__all__'
        # from rest_framework.validators import UniqueValidator
        # extra_kwargs = {
        #     'cabinet': {'validators': [UniqueValidator(
        #         queryset=Cabinet.objects.all(),
        #         message='请重新选择')]},
        # }

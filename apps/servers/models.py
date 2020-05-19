from django.db import models
from products.models import Product
from idcs.models import Idc
from cabinet.models import Cabinet
from manufacturers.models import Manufacturer, ProductModel
from users.models import User

# Create your models here.


class Server(models.Model):
    created_user    = models.CharField("创建者", max_length=32, null=True, blank=True, help_text="创建者")
    updated_user    = models.CharField("最后更新者", max_length=32, null=True, blank=True, help_text="最后更新者")
    manufacturer    = models.ForeignKey(Manufacturer, verbose_name="制造商", null=True, help_text="制造商")
    manufacture_data= models.DateField("制造日期", null=True, help_text="制造日期")
    model_name      = models.ForeignKey(ProductModel, verbose_name="服务器型号", null=True, blank=True, help_text="服务器型号")
    idc             = models.ForeignKey(Idc, verbose_name="所在机房", null=True, help_text="所在机房")
    cabinet         = models.ForeignKey(Cabinet, verbose_name="所在机柜", null=True, help_text="所在机柜")
    cabinet_position= models.CharField("机柜内位置", max_length=32, null=True, help_text="机柜内位置")
    warranty_time   = models.DateField("保修时间", null=True, help_text="保修时间")
    purchasing_time = models.DateField("采购时间", null=True, help_text="采购时间")
    power_supply    = models.IntegerField("电源功率", null=True, help_text="电源功率")
    os              = models.CharField("操作系统", max_length=100, null=True, help_text="操作系统")
    hostname        = models.CharField("主机名", max_length=50, default=None, db_index=True, unique=True, error_messages={"错误":"主机名重复"}, help_text="主机名")
    ip              = models.GenericIPAddressField("IP地址", max_length=32, default=None, db_index=True, unique=True, error_messages={"错误":"IP 重复"}, help_text="管理IP")
    eip             = models.CharField("EIP地址", max_length=32, null=True, default=None, blank=True, help_text="EIP")
    cpu_model       = models.CharField("CPU型号", max_length=250, null=True, help_text="CPU型号")
    cpu_core_count  = models.CharField("CPU核数", max_length=250, null=True, help_text="CPU核数")
    disk            = models.CharField("硬盘信息", max_length=300, null=True, help_text="硬盘信息")
    server_mem      = models.CharField("内存信息", max_length=100, null=True, help_text="内存信息")
    status          = models.CharField("服务器状态", max_length=32, null=True, db_index=True, blank=True, help_text="服务器状态")
    env             = models.CharField("服务器环境", max_length=32, null=True, db_index=True, blank=True, help_text="服务器环境")
    remark          = models.CharField("备注", max_length=200, null=True, unique=True, help_text="备注")
    service         = models.ForeignKey(Product, null=True, verbose_name="一级业务线", related_name="service", help_text="一级业务线")
    server_purpose  = models.ForeignKey(Product, null=True, verbose_name="二级产品线", related_name="server_purpose", help_text="二级产品线")
    created_time    = models.DateTimeField("创建时间", auto_now_add=True, editable=True, help_text="创建时间")
    updated_time    = models.DateTimeField("更新时间", auto_now=True, help_text="更新时间")
    instance_id     = models.CharField("InstanceID", max_length=100, db_index=True,null=True, unique=True, help_text="InstanceID")
    sn              = models.CharField("SN", max_length=40,db_index=True,null=True, help_text="SN")
    # rmt_card_ip     = models.CharField("远程管理卡IP", max_length=15, null=True, help_text="远程管理卡IP")
    server_type     = models.IntegerField("机器类型", db_index=True, default=0, help_text="机器类型")
    # 历史遗留问题解决字段方案：
    ImageId         = models.CharField("镜像 ID", max_length=100, null=True, help_text="镜像 ID")
    InstanceType    = models.CharField("实例类型", max_length=100, null=True, help_text="实例类型")
    SecurityGroupIds= models.CharField("安全组", max_length=100, null=True, help_text="安全组")
    VSwitchId       = models.CharField("交换机", max_length=100, null=True, help_text="交换机")



    """
        机器类型，0：云主机, 1:物理机, 2:虚拟机
    """

    def __str__(self):
        # return "{}[{}]".format(self.hostname, self.ip)
        return "{}".format(self.ip)

    class Meta:
        unique_together = [('hostname', 'ip')]
        db_table = 'resources_server'
        permissions=(
            ("view_server", "cat view server"),
        )

class NetworkDevice(models.Model):
    """
    网卡模型
    """
    name        = models.CharField("网卡设备名", max_length=32)
    mac         = models.CharField("网卡mac地址", max_length=32)
    host        = models.ForeignKey(Server, verbose_name="所在服务器")
    remark      = models.CharField("备注", max_length=300, null=True)

    def __str__(self):
        return "{}[{}]".format(self.name, self.host)
    class Meta:
        db_table = 'resources_networkdevice'
        permissions=(
            ("view_networkdevice", "cat view networkdevice"),
        )

class IP(models.Model):
    ip_addr     = models.CharField("ip地址", max_length=20, db_index=True)
    netmask     = models.CharField("子网掩码", max_length=20)
    device      = models.ForeignKey(NetworkDevice, verbose_name="网卡")

    def __str__(self):
        return self.ip_addr

    class Meta:
        db_table = 'resources_ip'
        permissions=(
            ("view_ip", "cat view ip"),
        )

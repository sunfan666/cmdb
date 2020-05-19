from django.db import models
from cabinet.models import Cabinet

class Vpcs(models.Model):
    """
    VPC模型
    """
    name        = models.CharField("专有网络名称", max_length=100, blank=True, help_text="专有网络名称")
    vpcid       = models.CharField("专有网络ID号", max_length=100, unique=True, blank=True, help_text="专有网络ID号")

    def __str__(self):
        return "{}[{}]".format(self.name, self.vpcid)
    class Meta:
        db_table = 'resources_vpcs'
        permissions=(
            ("view_vpc", "cat view vpc"),
        )

class Switches(models.Model):
    """
    Switch模型
    """
    name        = models.CharField("交换机名称", max_length=100, blank=True, help_text="交换机名称")
    switchid    = models.CharField("交换机ID号", max_length=100, unique=True, blank=True, help_text="交换机ID号")
    zone        = models.ForeignKey(Cabinet, verbose_name="所在分区", help_text="所在分区")
    vpc         = models.ForeignKey(Vpcs, verbose_name="所在VPC", help_text="所在VPC")

    def __str__(self):
        return "{}[{}]".format(self.name, self.vpc)
    class Meta:
        db_table = 'resources_switches'
        permissions=(
            ("view_switch", "cat view switch"),
        )

class SecurityGroups(models.Model):
    """
    Switch模型
    """
    name        = models.CharField("安全组名称", max_length=100, blank=True, help_text="安全组名称")
    segid       = models.CharField("安全组ID号", max_length=100, unique=True, blank=True, help_text="安全组ID号")
    vpc         = models.ForeignKey(Vpcs, verbose_name="所在VPC", help_text="所在VPC")

    def __str__(self):
        return "{}[{}]".format(self.name, self.vpc)
    class Meta:
        db_table = 'resources_securitygroups'
        permissions=(
            ("view_securitygroups", "cat view securitygroups"),
        )

class Images(models.Model):
    """
    Switch模型
    """
    imageowner  = models.CharField("镜像来源", max_length=100, blank=True, help_text="镜像来源")
    name        = models.CharField("镜像名称", max_length=100, blank=True, help_text="镜像名称")
    imageid     = models.CharField("镜像ID号", max_length=100, unique=True, blank=True, help_text="镜像ID号")

    def __str__(self):
        return "{}[{}]".format(self.name, self.imageid)
    class Meta:
        db_table = 'resources_images'
        permissions=(
            ("view_images", "cat view images"),
        )


class AvailableResources(models.Model):
    """
    InstanceType模型
    """
    typename    = models.CharField("规格名称", max_length=100, blank=True, help_text="规格名称")
    chinesename = models.CharField("中文解释", max_length=100, blank=True, help_text="中文解释")
    chargetype  = models.CharField("付费类型", max_length=100, blank=True, help_text="付费类型")
    cores       = models.IntegerField("核数", blank=True, null=True, help_text="核数")
    mems        = models.FloatField("内存数", blank=True, null=True, help_text="内存数")
    zone        = models.ForeignKey(Cabinet, verbose_name="所在分区", help_text="所在分区")

    def __str__(self):
        return "{}[{}]".format(self.typename, self.zone)
    class Meta:
        db_table = 'resources_instancetypes'
        permissions=(
            ("view_instancetype", "cat view instancetype"),
        )

class ResourceMatching(models.Model):
    """
    ResourceMatching模型
    """
    chargetype  = models.CharField("付费类型", max_length=100, blank=True, help_text="付费类型")
    cores       = models.IntegerField("核数", blank=True, null=True, help_text="核数")
    mems        = models.CharField("内存列表", max_length=100, blank=True, null=True, help_text="内存列表")
    zone        = models.ForeignKey(Cabinet, verbose_name="所在分区", help_text="所在分区")

    def __str__(self):
        return "{}[{}]".format(self.cores, self.mems, self.zone)
    class Meta:
        db_table = 'resources_resourcematching'
        permissions=(
            ("view_resourcematching", "cat view resourcematching"),
        )
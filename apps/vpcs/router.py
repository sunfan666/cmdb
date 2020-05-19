from rest_framework.routers import DefaultRouter
from .views import VpcViewset, SecurityGroupsViewset, SwitchViewset, \
    ImagesViewset, InstanceTypeViewset, ResourceMatchingViewset


vpcs_router = DefaultRouter()
vpcs_router.register(r'vpcs', VpcViewset, base_name="vpcs")
vpcs_router.register(r'Switches', SwitchViewset, base_name="Switches")
vpcs_router.register(r'segs', SecurityGroupsViewset, base_name="segs")
vpcs_router.register(r'images', ImagesViewset, base_name="images")
vpcs_router.register(r'instypes', InstanceTypeViewset, base_name="instypes")
vpcs_router.register(r'resmats', ResourceMatchingViewset, base_name="resmats")


from rest_framework.routers import DefaultRouter
from .views import ServerViewset, ServerListViewset, \
    NetwokDeviceViewset, IPViewset, ServerAutoReportViewset, \
    ServerCountViewset, VpcViewset, flushServerInfoViewset, \
    flushServerViewset, AddIdcViewset, Server2productViewset


servers_router = DefaultRouter()
servers_router.register(r'servers', ServerViewset, base_name="servers")
servers_router.register(r'serverlist', ServerListViewset, base_name="serverlist")
servers_router.register(r'addidcserver', AddIdcViewset, base_name="addidcserver")
servers_router.register(r'network_device', NetwokDeviceViewset, base_name="network_device")
servers_router.register(r'ip', IPViewset, base_name="ip")
servers_router.register(r'ServerAutoReport', ServerAutoReportViewset, base_name="ServerAutoReport")
servers_router.register(r'ServerCount', ServerCountViewset, base_name="ServerCount")
servers_router.register(r'Vpcinfos', VpcViewset, base_name="Vpcinfos")
servers_router.register(r'flushserverinfo', flushServerInfoViewset, base_name="flushserverinfo")
servers_router.register(r'flushserver', flushServerViewset, base_name="flushserver")
servers_router.register(r'addidcserver', AddIdcViewset, base_name="addidcserver")
servers_router.register(r'kuorongserver', Server2productViewset, base_name="kuorongserver")
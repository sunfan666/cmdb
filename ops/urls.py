"""ops URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls
from rest_framework_jwt.views import obtain_jwt_token



from users.router import user_router
from groups.router import group_router
from menu.router import menu_router
from cabinet.router import cabinet_router
from servers.router import servers_router
from idcs.router import idc_router
from vpcs.router import vpcs_router
from manufacturers.router import manufacturer_router
from permissions.router import permission_router
from products.router import products_router
from zabbix.router import zabbix_router

router = DefaultRouter()


router.registry.extend(user_router.registry)
router.registry.extend(group_router.registry)
router.registry.extend(idc_router.registry)
router.registry.extend(vpcs_router.registry)
router.registry.extend(menu_router.registry)
router.registry.extend(cabinet_router.registry)
router.registry.extend(servers_router.registry)
router.registry.extend(manufacturer_router.registry)
router.registry.extend(permission_router.registry)
router.registry.extend(products_router.registry)
router.registry.extend(zabbix_router.registry)


# urlpatterns = [
#     url(r'^admin/', admin.site.urls),
#     url(r'^api/', include(router.urls)),
#     url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
#     url(r'^api-token-auth/', obtain_jwt_token),
#     url(r'^docs/', include_docs_urls("Phoenix 资产系统"))
# ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# from rest_framework_swagger.views import get_swagger_view
#
# schema_view = get_swagger_view(title="Phoenix 资产系统")
#
# urlpatterns = [
#     url(r'^admin/', admin.site.urls),
#     url(r'^api/', include(router.urls)),
#     url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
#     url(r'^api-token-auth/', obtain_jwt_token),
#     url(r"^docs/$", schema_view)
# ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Phoenix 资产系统",
      default_version='v1',
      description="Phoenix 资产系统文档",
      terms_of_service="http://phoenix.xxxx.com/",
      contact=openapi.Contact(email="sunfan666@gmail.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^docs/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

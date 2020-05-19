from rest_framework.routers import DefaultRouter
from .views import ProductViewset, ProductsViewset, ProductManageViewSet, GroupProductViewset


products_router = DefaultRouter()
products_router.register(r'products', ProductsViewset, base_name='products')
products_router.register(r'productss', ProductViewset, base_name='productss')
products_router.register(r'productmanage', ProductManageViewSet, base_name="productmanage")
products_router.register(r'groupnode', GroupProductViewset, base_name="groupnode")
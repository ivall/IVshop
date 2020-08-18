from shop.api.viewsets import ServersViewSet, ProductsViewSet, ProductViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'product', ProductViewSet, basename='product')
urlpatterns = router.urls

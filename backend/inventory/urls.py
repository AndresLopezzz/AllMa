from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusinessTemplateViewSet, InventoryViewSet, ProductViewSet, DashboardView, AlertView

# El Router de DRF genera automáticamente las URLs para los ViewSets
# Por ejemplo, BusinessTemplateViewSet genera:
# - GET/POST     /api/templates/
# - GET/PUT/PATCH/DELETE  /api/templates/{id}/
# - POST         /api/templates/{id}/toggle_active/  (acción personalizada)

router = DefaultRouter()
router.register(r'templates', BusinessTemplateViewSet, basename='template')
router.register(r'inventories', InventoryViewSet, basename='inventory')
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('alerts/', AlertView.as_view(), name='alerts'),
]

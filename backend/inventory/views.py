from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import BusinessTemplate, Inventory, Product
from .serializers import (
    BusinessTemplateSerializer,
    InventoryListSerializer,
    InventoryDetailSerializer,
    ProductSerializer
)


class BusinessTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar BusinessTemplates (Plantillas de negocio).

    Endpoints generados automáticamente:
    - GET /api/templates/ - Lista todas las plantillas activas
    - POST /api/templates/ - Crea una nueva plantilla (solo admin)
    - GET /api/templates/{id}/ - Detalle de una plantilla
    - PUT /api/templates/{id}/ - Actualiza una plantilla (solo admin/creador)
    - PATCH /api/templates/{id}/ - Actualización parcial (solo admin/creador)
    - DELETE /api/templates/{id}/ - Elimina una plantilla (solo admin)

    Permisos:
    - Cualquier usuario autenticado puede VER plantillas
    - Solo admin puede CREAR/MODIFICAR/ELIMINAR
    """
    serializer_class = BusinessTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']  # Por defecto, las más recientes primero

    def get_queryset(self):
        """
        Retorna solo plantillas activas.
        Los admins pueden ver todas con ?show_inactive=true
        """
        queryset = BusinessTemplate.objects.select_related('created_by')

        # Si el usuario es admin y pasa show_inactive=true, mostrar todas
        if self.request.user.is_staff and self.request.query_params.get('show_inactive'):
            return queryset

        # Por defecto, solo activas
        return queryset.filter(is_active=True)

    def perform_create(self, serializer):
        """
        Al crear una plantilla, asignar automáticamente el usuario actual como created_by.
        Este método se llama automáticamente cuando se hace POST.
        """
        serializer.save(created_by=self.request.user)

    def get_permissions(self):
        """
        Define permisos según la acción:
        - list, retrieve: cualquier usuario autenticado
        - create, update, partial_update, destroy: solo admin
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def toggle_active(self, request, pk=None):
        """
        Endpoint personalizado para activar/desactivar una plantilla.
        POST /api/templates/{id}/toggle_active/
        """
        template = self.get_object()
        template.is_active = not template.is_active
        template.save()
        serializer = self.get_serializer(template)
        return Response({
            'message': f'Plantilla {"activada" if template.is_active else "desactivada"}',
            'data': serializer.data
        })


class InventoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Inventarios.

    Cada usuario solo puede ver/editar sus propios inventarios.
    Admins pueden ver todos.
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['template']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Cada usuario solo ve sus propios inventarios.
        Admins ven todos.
        """
        user = self.request.user
        if user.is_staff:
            return Inventory.objects.select_related('owner', 'template')
        return Inventory.objects.filter(owner=user).select_related('owner', 'template')

    def get_serializer_class(self):
        """
        Usa serializers diferentes según la acción:
        - list: InventoryListSerializer (ligero)
        - retrieve, create, update: InventoryDetailSerializer (completo)
        """
        if self.action == 'list':
            return InventoryListSerializer
        return InventoryDetailSerializer

    def perform_create(self, serializer):
        """
        Al crear un inventario, asignar automáticamente el usuario actual como owner.
        """
        serializer.save(owner=self.request.user)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Productos.

    Cada usuario solo puede gestionar productos de sus propios inventarios.
    Soporta filtros por inventario, categoría y estado de stock.
    """
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['inventory', 'category']
    search_fields = ['name', 'sku', 'description']
    ordering_fields = ['name', 'sku', 'quantity', 'price', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        """
        Cada usuario solo ve productos de sus propios inventarios.
        Admins ven todos.

        Filtros adicionales:
        - ?low_stock=true - Solo productos con stock bajo
        - ?out_of_stock=true - Solo productos sin stock
        """
        user = self.request.user

        if user.is_staff:
            queryset = Product.objects.select_related('inventory')
        else:
            queryset = Product.objects.filter(inventory__owner=user).select_related('inventory')

        # Filtro por stock bajo
        if self.request.query_params.get('low_stock') == 'true':
            # Filtramos productos donde quantity <= low_stock_threshold Y quantity > 0
            from django.db.models import F
            queryset = queryset.filter(quantity__lte=F('low_stock_threshold'), quantity__gt=0)

        # Filtro por sin stock
        if self.request.query_params.get('out_of_stock') == 'true':
            queryset = queryset.filter(quantity=0)

        return queryset

    def perform_create(self, serializer):
        """
        Validar que el inventario pertenezca al usuario antes de crear el producto.
        """
        inventory = serializer.validated_data.get('inventory')

        # Verificar que el usuario sea dueño del inventario
        if not self.request.user.is_staff and inventory.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("No puedes agregar productos a un inventario que no te pertenece")

        serializer.save()

    def perform_update(self, serializer):
        """
        Validar permisos al actualizar un producto.
        """
        instance = self.get_object()

        # Verificar que el usuario sea dueño del inventario
        if not self.request.user.is_staff and instance.inventory.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("No puedes modificar productos de un inventario que no te pertenece")

        serializer.save()

    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        """
        Endpoint para ajustar el stock de un producto.
        POST /api/products/{id}/adjust_stock/
        Body: {"adjustment": 10} o {"adjustment": -5}
        """
        product = self.get_object()

        # Validar permisos
        if not request.user.is_staff and product.inventory.owner != request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("No tienes permiso para ajustar este producto")

        # Obtener ajuste
        adjustment = request.data.get('adjustment')
        if adjustment is None:
            return Response(
                {'error': 'Debes proporcionar un valor de "adjustment"'},
                status=400
            )

        try:
            adjustment = int(adjustment)
        except (ValueError, TypeError):
            return Response(
                {'error': 'El ajuste debe ser un número entero'},
                status=400
            )

        # Aplicar ajuste
        new_quantity = product.quantity + adjustment
        if new_quantity < 0:
            return Response(
                {'error': f'El ajuste resultaría en cantidad negativa ({new_quantity})'},
                status=400
            )

        product.quantity = new_quantity
        product.save()

        serializer = self.get_serializer(product)
        return Response({
            'message': f'Stock ajustado: {adjustment:+d}',
            'previous_quantity': product.quantity - adjustment,
            'current_quantity': product.quantity,
            'data': serializer.data
        })

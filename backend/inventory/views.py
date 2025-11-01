from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import BusinessTemplate, Inventory, Product
from .serializers import (
    BusinessTemplateSerializer,
    InventoryListSerializer,
    InventoryDetailSerializer,
    ProductSerializer
)
from .filters import ProductFilter
from .utils import validate_custom_fields_structure, check_plan_limits


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
        Valida límites del plan antes de crear.
        """
        # Verificar límites del plan
        can_create, error_message = check_plan_limits(self.request.user, 'create_inventory')
        if not can_create:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                'error': error_message,
                'error_code': 'plan_limit_exceeded',
                'upgrade_required': True
            })

        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['put'], url_path='custom-fields')
    def custom_fields(self, request, pk=None):
        """
        Endpoint para personalizar los custom_fields de un inventario específico.

        PUT /api/inventories/{id}/custom-fields/

        Body: {
            "custom_fields": {
                "marca": {"type": "text", "required": true},
                "color": {"type": "select", "required": false, "options": ["rojo", "azul"]}
            }
        }

        O en formato lista:
        {
            "custom_fields": [
                {"name": "marca", "type": "text", "required": true},
                {"name": "color", "type": "select", "required": false, "options": ["rojo", "azul"]}
            ]
        }

        Prioridad:
        - Si custom_template_fields existe, se usa para validar nuevos productos
        - Sino, se usa template.custom_fields de la plantilla base

        Nota: Los productos existentes NO se ven afectados por este cambio.
        """
        inventory = self.get_object()

        # Verificar permisos: solo el dueño puede modificar
        if not request.user.is_staff and inventory.owner != request.user:
            return Response(
                {'error': 'No tienes permiso para modificar este inventario'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Obtener custom_fields del body
        custom_fields = request.data.get('custom_fields')

        if custom_fields is None:
            return Response(
                {'error': 'Debes proporcionar "custom_fields" en el body'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar estructura
        is_valid, error_message = validate_custom_fields_structure(custom_fields)
        if not is_valid:
            return Response(
                {'error': f'Estructura de custom_fields inválida: {error_message}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Guardar en inventory.custom_template_fields
        inventory.custom_template_fields = custom_fields
        inventory.save()

        # Retornar respuesta con el inventario actualizado
        serializer = InventoryDetailSerializer(inventory)
        return Response({
            'message': 'Plantilla personalizada actualizada exitosamente',
            'data': serializer.data,
            'effective_template': custom_fields
        }, status=status.HTTP_200_OK)


class ProductPagination(PageNumberPagination):
    """
    Paginación personalizada para productos: 20 items por página.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Productos.

    Cada usuario solo puede gestionar productos de sus propios inventarios.

    Filtros disponibles:
    - search: Busca en nombre o SKU
    - category: Filtra por categoría
    - inventory: Filtra por ID de inventario
    - low_stock: Productos con stock bajo (quantity < low_stock_threshold)
    - template: Filtra por ID de plantilla

    Ordenamiento disponible (?ordering=):
    - name, -name
    - price, -price
    - created_at, -created_at
    - quantity, -quantity
    - sku, -sku

    Paginación: 20 items por página
    """
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ProductFilter
    ordering_fields = ['name', 'sku', 'quantity', 'price', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        """
        Cada usuario solo ve productos de sus propios inventarios.
        Admins ven todos.

        Filtros adicionales:
        - ?include_inactive=true - Incluir productos eliminados (soft delete)
        """
        user = self.request.user

        if user.is_staff:
            queryset = Product.objects.select_related('inventory')
        else:
            queryset = Product.objects.filter(inventory__owner=user).select_related('inventory')

        # Por defecto, solo mostrar productos activos (no eliminados)
        if not self.request.query_params.get('include_inactive'):
            queryset = queryset.filter(is_active=True)

        return queryset

    def perform_create(self, serializer):
        """
        Validar que el inventario pertenezca al usuario antes de crear el producto.
        Valida límites del plan antes de crear.
        """
        inventory = serializer.validated_data.get('inventory')

        # Verificar que el usuario sea dueño del inventario
        if not self.request.user.is_staff and inventory.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("No puedes agregar productos a un inventario que no te pertenece")

        # Verificar límites del plan
        can_create, error_message = check_plan_limits(self.request.user, 'create_product')
        if not can_create:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                'error': error_message,
                'error_code': 'plan_limit_exceeded',
                'upgrade_required': True
            })

        serializer.save()

    def perform_update(self, serializer):
        """
        Validar permisos al actualizar un producto.
        Las validaciones de custom_data se ejecutan automáticamente en el serializer.
        """
        instance = self.get_object()

        # Verificar que el usuario sea dueño del inventario
        if not self.request.user.is_staff and instance.inventory.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("No puedes modificar productos de un inventario que no te pertenece")

        serializer.save()

    def perform_destroy(self, instance):
        """
        Soft delete: en lugar de eliminar, marca como is_active=False.
        Los admins pueden usar ?hard_delete=true para eliminar permanentemente.
        """
        # Verificar permisos
        if not self.request.user.is_staff and instance.inventory.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("No puedes eliminar productos de un inventario que no te pertenece")

        # Hard delete solo para admins si lo solicitan explícitamente
        if self.request.user.is_staff and self.request.query_params.get('hard_delete') == 'true':
            instance.delete()
        else:
            # Soft delete: marcar como inactivo
            instance.is_active = False
            instance.save()

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """
        Restaurar un producto eliminado (soft delete).
        POST /api/products/{id}/restore/
        """
        product = self.get_object()

        # Verificar permisos
        if not request.user.is_staff and product.inventory.owner != request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("No tienes permiso para restaurar este producto")

        # Verificar si ya está activo
        if product.is_active:
            return Response(
                {'error': 'El producto ya está activo'},
                status=400
            )

        # Restaurar producto
        product.is_active = True
        product.save()

        serializer = self.get_serializer(product)
        return Response({
            'message': 'Producto restaurado exitosamente',
            'data': serializer.data
        })

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

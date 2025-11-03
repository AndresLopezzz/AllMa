from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q, F, DecimalField
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from decimal import Decimal
from .models import BusinessTemplate, Inventory, Product, Movement
import csv
from .serializers import (
    BusinessTemplateSerializer,
    InventoryListSerializer,
    InventoryDetailSerializer,
    ProductSerializer,
    AlertSerializer
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

    @action(detail=True, methods=['get'], url_path='export')
    def export(self, request, pk=None):
        """
        Exporta todos los productos de un inventario a CSV.

        GET /api/inventories/{id}/export/

        Genera un archivo CSV con:
        - Columnas estándar: SKU, Nombre, Descripción, Cantidad, Precio, Categoría, Stock Status
        - Columnas de custom_data aplanadas dinámicamente

        Returns:
            CSV file con content-type: text/csv
        """
        inventory = self.get_object()

        # Verificar permisos: solo el dueño puede exportar
        if not request.user.is_staff and inventory.owner != request.user:
            return Response(
                {'error': 'No tienes permiso para exportar este inventario'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Obtener todos los productos activos del inventario
        products = Product.objects.filter(
            inventory=inventory,
            is_active=True
        ).order_by('sku')

        # Crear respuesta HTTP con tipo CSV
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="inventario_{inventory.id}_{inventory.name}.csv"'

        # Agregar BOM para que Excel reconozca UTF-8
        response.write('\ufeff')

        writer = csv.writer(response)

        # Determinar todas las columnas de custom_data
        custom_keys = set()
        for product in products:
            if product.custom_data:
                custom_keys.update(product.custom_data.keys())
        custom_keys = sorted(custom_keys)

        # Escribir encabezados
        headers = [
            'SKU',
            'Nombre',
            'Descripción',
            'Cantidad',
            'Precio',
            'Umbral Stock Bajo',
            'Categoría',
            'Estado Stock',
            'Fecha Creación',
            'Última Actualización'
        ]

        # Agregar columnas personalizadas
        for key in custom_keys:
            headers.append(f'Custom: {key}')

        writer.writerow(headers)

        # Escribir datos de productos
        for product in products:
            row = [
                product.sku,
                product.name,
                product.description or '',
                product.quantity,
                float(product.price),
                product.low_stock_threshold,
                product.category or '',
                product.stock_status,
                product.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                product.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            ]

            # Agregar valores de custom_data
            for key in custom_keys:
                value = product.custom_data.get(key, '') if product.custom_data else ''
                row.append(value)

            writer.writerow(row)

        return response

    @action(detail=True, methods=['get'], url_path='stats')
    def stats(self, request, pk=None):
        """
        Retorna estadísticas detalladas de un inventario específico.

        GET /api/inventories/{id}/stats/

        Response:
        {
            "inventory_id": 1,
            "inventory_name": "Bodega Principal",
            "total_products": 150,
            "total_value": 45000.00,
            "low_stock_products": 5,
            "out_of_stock_products": 2,
            "categories": [
                {"name": "Electrónica", "count": 30, "total_value": 15000.00},
                ...
            ],
            "top_products_by_value": [
                {"id": 1, "name": "...", "sku": "...", "value": 1000.00},
                ...
            ],
            "recent_movements": [
                {"id": 1, "type": "entrada", "quantity": 10, ...},
                ...
            ],
            "stock_distribution": {
                "in_stock": 100,
                "low_stock": 40,
                "out_of_stock": 10
            }
        }
        """
        inventory = self.get_object()

        # Verificar permisos
        if not request.user.is_staff and inventory.owner != request.user:
            return Response(
                {'error': 'No tienes permiso para ver estadísticas de este inventario'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Obtener productos activos del inventario
        products = Product.objects.filter(
            inventory=inventory,
            is_active=True
        )

        # Métricas básicas
        total_products = products.count()

        # Valor total del inventario (cantidad * precio)
        total_value = products.annotate(
            product_value=F('quantity') * F('price')
        ).aggregate(
            total=Coalesce(Sum('product_value'), Decimal('0.00'))
        )['total']

        # Productos con stock bajo y sin stock
        low_stock_count = products.filter(
            quantity__lte=F('low_stock_threshold'),
            quantity__gt=0
        ).count()

        out_of_stock_count = products.filter(quantity=0).count()

        # Distribución de stock
        in_stock_count = products.filter(
            quantity__gt=F('low_stock_threshold')
        ).count()

        # Estadísticas por categoría
        categories_stats = products.values('category').annotate(
            count=Count('id'),
            total_value=Sum(F('quantity') * F('price'), output_field=DecimalField())
        ).order_by('-total_value')

        categories_list = []
        for cat in categories_stats:
            categories_list.append({
                'name': cat['category'] if cat['category'] else 'Sin categoría',
                'count': cat['count'],
                'total_value': float(cat['total_value'] or 0)
            })

        # Top 10 productos por valor (cantidad * precio)
        top_products = products.annotate(
            product_value=F('quantity') * F('price')
        ).order_by('-product_value')[:10]

        top_products_list = []
        for product in top_products:
            top_products_list.append({
                'id': product.id,
                'name': product.name,
                'sku': product.sku,
                'quantity': product.quantity,
                'price': float(product.price),
                'total_value': float(product.quantity * product.price),
                'category': product.category or 'Sin categoría'
            })

        # Movimientos recientes (últimos 10)
        recent_movements = Movement.objects.filter(
            product__inventory=inventory
        ).select_related('product', 'performed_by').order_by('-timestamp')[:10]

        recent_movements_list = []
        for movement in recent_movements:
            recent_movements_list.append({
                'id': movement.id,
                'product_name': movement.product.name,
                'product_sku': movement.product.sku,
                'movement_type': movement.movement_type,
                'quantity': movement.quantity,
                'quantity_before': movement.quantity_before,
                'quantity_after': movement.quantity_after,
                'reason': movement.reason,
                'performed_by': movement.performed_by.email if movement.performed_by else None,
                'timestamp': movement.timestamp.isoformat()
            })

        # Construir respuesta
        data = {
            'inventory_id': inventory.id,
            'inventory_name': inventory.name,
            'total_products': total_products,
            'total_value': float(total_value),
            'low_stock_products': low_stock_count,
            'out_of_stock_products': out_of_stock_count,
            'stock_distribution': {
                'in_stock': in_stock_count,
                'low_stock': low_stock_count,
                'out_of_stock': out_of_stock_count
            },
            'categories': categories_list,
            'top_products_by_value': top_products_list,
            'recent_movements': recent_movements_list
        }

        return Response(data, status=status.HTTP_200_OK)


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
    parser_classes = [MultiPartParser, FormParser, JSONParser]
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

        # Actualizar cantidad y registrar quién hizo el ajuste
        product.quantity = new_quantity
        product._performed_by = request.user
        product.save()

        serializer = self.get_serializer(product)
        return Response({
            'message': f'Stock ajustado: {adjustment:+d}',
            'previous_quantity': product.quantity - adjustment,
            'current_quantity': product.quantity,
            'data': serializer.data
        })


class DashboardView(APIView):
    """
    Vista para obtener métricas del dashboard.

    GET /api/dashboard/

    Query params opcionales:
    - inventory: ID del inventario para filtrar métricas

    Retorna:
    - total_products: Cantidad de productos activos
    - total_inventory_value: Valor total del inventario (precio * cantidad)
    - low_stock_count: Cantidad de productos con stock bajo
    - total_inventories: Cantidad de inventarios del usuario
    - recent_movements: Últimos 10 movimientos (opcional)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        inventory_id = request.query_params.get('inventory')

        # Base queryset: solo productos del usuario
        if user.is_staff:
            products_queryset = Product.objects.select_related('inventory')
        else:
            products_queryset = Product.objects.filter(
                inventory__owner=user
            ).select_related('inventory')

        # Filtrar por inventario específico si se proporciona
        if inventory_id:
            products_queryset = products_queryset.filter(inventory_id=inventory_id)

        # Solo productos activos
        products_queryset = products_queryset.filter(is_active=True)

        # Métricas básicas
        total_products = products_queryset.count()

        # Valor total del inventario (precio * cantidad)
        inventory_value_data = products_queryset.aggregate(
            total_value=Sum(F('price') * F('quantity'))
        )
        total_inventory_value = inventory_value_data['total_value'] or 0

        # Productos con stock bajo (quantity <= low_stock_threshold)
        low_stock_count = products_queryset.filter(
            quantity__lte=F('low_stock_threshold')
        ).count()

        # Productos sin stock
        out_of_stock_count = products_queryset.filter(quantity=0).count()

        # Total de inventarios del usuario
        if user.is_staff:
            total_inventories = Inventory.objects.count()
        else:
            inventories_queryset = Inventory.objects.filter(owner=user)
            if inventory_id:
                inventories_queryset = inventories_queryset.filter(id=inventory_id)
            total_inventories = inventories_queryset.count()

        # Construir respuesta
        data = {
            'total_products': total_products,
            'total_inventory_value': float(total_inventory_value),
            'low_stock_count': low_stock_count,
            'out_of_stock_count': out_of_stock_count,
            'total_inventories': total_inventories,
        }

        # Si se filtró por inventario, agregar info del inventario
        if inventory_id:
            try:
                if user.is_staff:
                    inventory = Inventory.objects.get(id=inventory_id)
                else:
                    inventory = Inventory.objects.get(id=inventory_id, owner=user)

                data['inventory'] = {
                    'id': inventory.id,
                    'name': inventory.name,
                    'template_name': inventory.template.name
                }
            except Inventory.DoesNotExist:
                pass

        # Datos para gráficas

        # 1. Productos por categoría
        products_by_category = products_queryset.values('category').annotate(
            count=Count('id')
        ).order_by('-count')

        # Convertir a lista y manejar categorías vacías
        products_by_category_list = []
        for item in products_by_category:
            category_name = item['category'] if item['category'] else 'Sin categoría'
            products_by_category_list.append({
                'category': category_name,
                'count': item['count']
            })

        data['products_by_category'] = products_by_category_list

        # 2. Valor por inventario
        if user.is_staff:
            inventories_queryset = Inventory.objects.all()
        else:
            inventories_queryset = Inventory.objects.filter(owner=user)

        # Si se filtró por inventario, solo mostrar ese
        if inventory_id:
            inventories_queryset = inventories_queryset.filter(id=inventory_id)

        value_by_inventory_list = []
        for inv in inventories_queryset:
            inv_products = products_queryset.filter(inventory=inv)
            inv_value = inv_products.aggregate(
                total=Coalesce(Sum(F('price') * F('quantity')), 0, output_field=DecimalField())
            )['total']

            value_by_inventory_list.append({
                'inventory_id': inv.id,
                'inventory_name': inv.name,
                'value': float(inv_value)
            })

        # Ordenar por valor descendente
        value_by_inventory_list.sort(key=lambda x: x['value'], reverse=True)
        data['value_by_inventory'] = value_by_inventory_list

        # 3. Movimientos recientes (últimos 10)
        movements_queryset = Movement.objects.select_related(
            'product', 'product__inventory', 'performed_by'
        ).filter(
            product__inventory__in=inventories_queryset
        ).order_by('-timestamp')[:10]

        recent_movements_list = []
        for movement in movements_queryset:
            recent_movements_list.append({
                'id': movement.id,
                'product_id': movement.product.id,
                'product_name': movement.product.name,
                'product_sku': movement.product.sku,
                'inventory_name': movement.product.inventory.name,
                'movement_type': movement.movement_type,
                'movement_type_display': movement.get_movement_type_display(),
                'quantity': movement.quantity,
                'quantity_before': movement.quantity_before,
                'quantity_after': movement.quantity_after,
                'reason': movement.reason,
                'performed_by': movement.performed_by.email if movement.performed_by else None,
                'timestamp': movement.timestamp.isoformat()
            })

        data['recent_movements'] = recent_movements_list

        return Response(data, status=status.HTTP_200_OK)


class AlertPagination(PageNumberPagination):
    """
    Paginación específica para alertas.
    10 alertas por página.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class AlertView(APIView):
    """
    Vista para listar productos con stock bajo (alertas).

    GET /api/alerts/
        Lista productos con quantity < low_stock_threshold
        Ordenados por criticidad (ratio más bajo = más crítico)

    Query parameters:
        - page: número de página (default: 1)
        - page_size: tamaño de página (default: 10, max: 50)
        - inventory: filtrar por ID de inventario
        - new_only: si es 'true', solo muestra alertas no enviadas (alert_sent=False)
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = AlertPagination

    def get(self, request):
        """
        Lista productos con stock bajo ordenados por criticidad.
        """
        # Base queryset: productos con stock bajo
        queryset = Product.objects.filter(
            is_active=True,
            quantity__lt=F('low_stock_threshold')
        ).select_related(
            'inventory',
            'inventory__owner'
        )

        # Filtrar por inventarios del usuario (no admin ve solo sus inventarios)
        if not request.user.is_staff:
            queryset = queryset.filter(inventory__owner=request.user)

        # Filtro opcional: por inventario específico
        inventory_id = request.query_params.get('inventory')
        if inventory_id:
            queryset = queryset.filter(inventory_id=inventory_id)

        # Filtro opcional: solo alertas nuevas (no enviadas)
        new_only = request.query_params.get('new_only', '').lower() == 'true'
        if new_only:
            queryset = queryset.filter(alert_sent=False)

        # Anotar el ratio de criticidad para ordenar
        # Usamos F() para calcular en la base de datos
        # Agregamos un pequeño valor para evitar división por cero
        queryset = queryset.annotate(
            criticality=F('quantity') * 1.0 / (F('low_stock_threshold') + 0.0001)
        ).order_by('criticality', 'quantity')

        # Paginar
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = AlertSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        # Si no hay paginación (no debería pasar)
        serializer = AlertSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

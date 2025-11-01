from django_filters import rest_framework as filters
from django.db.models import F
from .models import Product


class ProductFilter(filters.FilterSet):
    """
    Filtro avanzado para productos.

    Filtros disponibles:
    - search: Busca en nombre o SKU (ej: ?search=cable)
    - category: Filtra por categoría exacta (ej: ?category=electrónica)
    - inventory: Filtra por ID de inventario (ej: ?inventory=1)
    - low_stock: Productos con stock bajo (quantity <= low_stock_threshold) (ej: ?low_stock=true)
    - template: Filtra por ID de plantilla del inventario (ej: ?template=2)
    """

    # Búsqueda en nombre o SKU
    search = filters.CharFilter(method='filter_search', label='Buscar en nombre o SKU')

    # Filtro por categoría (exacto)
    category = filters.CharFilter(field_name='category', lookup_expr='iexact', label='Categoría')

    # Filtro por inventario
    inventory = filters.NumberFilter(field_name='inventory', label='ID de Inventario')

    # Filtro por stock bajo
    low_stock = filters.BooleanFilter(method='filter_low_stock', label='Stock bajo')

    # Filtro por plantilla (a través de inventory__template)
    template = filters.NumberFilter(field_name='inventory__template', label='ID de Plantilla')

    class Meta:
        model = Product
        fields = ['search', 'category', 'inventory', 'low_stock', 'template']

    def filter_search(self, queryset, name, value):
        """
        Busca el término en nombre o SKU (case-insensitive).
        """
        return queryset.filter(
            name__icontains=value
        ) | queryset.filter(
            sku__icontains=value
        )

    def filter_low_stock(self, queryset, name, value):
        """
        Filtra productos con stock bajo si value=True.
        Stock bajo = quantity < low_stock_threshold
        """
        if value:
            return queryset.filter(quantity__lt=F('low_stock_threshold'))
        return queryset

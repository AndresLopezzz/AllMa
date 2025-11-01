"""
Constantes para el módulo de inventario
"""

# Límites por tipo de plan
PLAN_LIMITS = {
    'free': {
        'max_products': 100,
        'max_inventories': 1,
        'description': 'Plan gratuito con límites básicos'
    },
    'pro': {
        'max_products': 1000,
        'max_inventories': 5,
        'description': 'Plan profesional para pequeños negocios'
    },
    'premium': {
        'max_products': -1,  # -1 significa ilimitado
        'max_inventories': -1,  # -1 significa ilimitado
        'description': 'Plan premium sin límites'
    }
}

# Tipos de validación
VALIDATION_ERRORS = {
    'PLAN_LIMIT_EXCEEDED': 'plan_limit_exceeded',
    'INVALID_QUANTITY': 'invalid_quantity',
    'INVALID_PRICE': 'invalid_price',
    'DUPLICATE_SKU': 'duplicate_sku',
}

# Mensajes de error
ERROR_MESSAGES = {
    'products_limit_exceeded': 'Has alcanzado el límite de productos para tu plan {plan}. Límite: {limit}',
    'inventories_limit_exceeded': 'Has alcanzado el límite de inventarios para tu plan {plan}. Límite: {limit}',
    'quantity_negative': 'La cantidad no puede ser negativa',
    'price_invalid': 'El precio debe ser mayor a 0',
    'sku_duplicate': 'Ya existe un producto con este SKU en este inventario',
    'upgrade_required': 'Actualiza tu plan para crear más {resource}',
}

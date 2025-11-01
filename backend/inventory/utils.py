"""
Utilidades para el módulo de inventario
"""
from typing import Dict, Any, Union, List


def get_effective_template(inventory) -> Dict[str, Any]:
    """
    Retorna los custom_fields efectivos para un inventario.

    Prioridad:
    1. Si el inventario tiene custom_template_fields personalizado → usar ese
    2. Sino → usar template.custom_fields de la plantilla base

    Args:
        inventory: Instancia del modelo Inventory

    Returns:
        dict: Estructura de custom_fields a usar para validar productos

    Examples:
        >>> inventory = Inventory.objects.get(id=1)
        >>> fields = get_effective_template(inventory)
        >>> print(fields)
        {
            "marca": {"type": "text", "required": true},
            "color": {"type": "select", "required": false, "options": ["rojo", "azul"]}
        }
    """
    # Si el inventario tiene una plantilla personalizada, usarla
    if inventory.custom_template_fields:
        return inventory.custom_template_fields

    # Sino, usar la plantilla base del template
    if inventory.template and inventory.template.custom_fields:
        return inventory.template.custom_fields

    # Si no hay ninguna, retornar diccionario vacío
    return {}


def validate_custom_fields_structure(custom_fields: Union[Dict, List]) -> tuple[bool, str]:
    """
    Valida que la estructura de custom_fields sea correcta.

    Soporta dos formatos:
    1. Diccionario: {"campo": {"type": "text", "required": true}, ...}
    2. Lista: [{"name": "campo", "type": "text", "required": true}, ...]

    Args:
        custom_fields: Estructura a validar

    Returns:
        tuple: (es_valido: bool, mensaje_error: str)

    Examples:
        >>> is_valid, error = validate_custom_fields_structure({
        ...     "marca": {"type": "text", "required": True}
        ... })
        >>> print(is_valid)
        True
    """
    if not custom_fields:
        return True, ""

    # Validar formato lista
    if isinstance(custom_fields, list):
        for idx, field in enumerate(custom_fields):
            if not isinstance(field, dict):
                return False, f"Campo en posición {idx} debe ser un diccionario"

            # Validar que tenga 'name'
            if 'name' not in field:
                return False, f"Campo en posición {idx} debe tener 'name'"

            # Validar que tenga 'type'
            if 'type' not in field:
                return False, f"Campo '{field.get('name', idx)}' debe tener 'type'"

            # Validar tipo
            valid_types = ['text', 'number', 'select', 'checkbox', 'date', 'textarea']
            if field['type'] not in valid_types:
                return False, f"Campo '{field['name']}': tipo '{field['type']}' no válido. Tipos válidos: {valid_types}"

            # Si es select, debe tener options
            if field['type'] == 'select' and 'options' not in field:
                return False, f"Campo '{field['name']}' de tipo 'select' debe tener 'options'"

            # Validar que options sea una lista
            if field['type'] == 'select' and not isinstance(field.get('options'), list):
                return False, f"Campo '{field['name']}': 'options' debe ser una lista"

    # Validar formato diccionario
    elif isinstance(custom_fields, dict):
        for field_name, field_config in custom_fields.items():
            if not isinstance(field_config, dict):
                return False, f"Configuración del campo '{field_name}' debe ser un diccionario"

            # Validar que tenga 'type'
            if 'type' not in field_config:
                return False, f"Campo '{field_name}' debe tener 'type'"

            # Validar tipo
            valid_types = ['text', 'number', 'select', 'checkbox', 'date', 'textarea']
            if field_config['type'] not in valid_types:
                return False, f"Campo '{field_name}': tipo '{field_config['type']}' no válido. Tipos válidos: {valid_types}"

            # Si es select, debe tener options
            if field_config['type'] == 'select' and 'options' not in field_config:
                return False, f"Campo '{field_name}' de tipo 'select' debe tener 'options'"

            # Validar que options sea una lista
            if field_config['type'] == 'select' and not isinstance(field_config.get('options'), list):
                return False, f"Campo '{field_name}': 'options' debe ser una lista"
    else:
        return False, "custom_fields debe ser un diccionario o una lista"

    return True, ""


def normalize_custom_fields(custom_fields: Union[Dict, List]) -> Dict[str, Any]:
    """
    Normaliza custom_fields de cualquier formato a formato diccionario.

    Convierte formato lista a formato diccionario para facilitar procesamiento.

    Args:
        custom_fields: Estructura en formato lista o diccionario

    Returns:
        dict: custom_fields en formato diccionario

    Examples:
        >>> lista = [{"name": "marca", "type": "text", "required": True}]
        >>> resultado = normalize_custom_fields(lista)
        >>> print(resultado)
        {"marca": {"type": "text", "required": True}}
    """
    if isinstance(custom_fields, list):
        # Convertir lista a diccionario
        normalized = {}
        for field in custom_fields:
            field_name = field.pop('name')
            normalized[field_name] = field
        return normalized

    # Ya es diccionario
    return custom_fields


def check_plan_limits(user, action: str) -> tuple[bool, str]:
    """
    Verifica si el usuario puede realizar una acción según los límites de su plan.

    Args:
        user: Instancia del modelo User
        action: 'create_product' o 'create_inventory'

    Returns:
        tuple: (puede_realizar: bool, mensaje_error: str)

    Examples:
        >>> can_create, error = check_plan_limits(user, 'create_product')
        >>> if not can_create:
        ...     return Response({'error': error}, status=402)
    """
    from .constants import PLAN_LIMITS, ERROR_MESSAGES
    from .models import Product, Inventory

    # Obtener límites del plan del usuario
    user_plan = user.plan if hasattr(user, 'plan') else 'free'
    limits = PLAN_LIMITS.get(user_plan, PLAN_LIMITS['free'])

    if action == 'create_product':
        max_products = limits['max_products']

        # -1 significa ilimitado
        if max_products == -1:
            return True, ""

        # Contar productos actuales del usuario
        current_count = Product.objects.filter(
            inventory__owner=user,
            is_active=True
        ).count()

        if current_count >= max_products:
            message = ERROR_MESSAGES['products_limit_exceeded'].format(
                plan=user_plan,
                limit=max_products
            )
            return False, message

        return True, ""

    elif action == 'create_inventory':
        max_inventories = limits['max_inventories']

        # -1 significa ilimitado
        if max_inventories == -1:
            return True, ""

        # Contar inventarios actuales del usuario
        current_count = Inventory.objects.filter(owner=user).count()

        if current_count >= max_inventories:
            message = ERROR_MESSAGES['inventories_limit_exceeded'].format(
                plan=user_plan,
                limit=max_inventories
            )
            return False, message

        return True, ""

    return True, ""


def get_user_usage(user) -> dict:
    """
    Obtiene el uso actual del usuario comparado con los límites de su plan.

    Args:
        user: Instancia del modelo User

    Returns:
        dict: Información de uso y límites

    Examples:
        >>> usage = get_user_usage(user)
        >>> print(usage)
        {
            "plan": "free",
            "products_count": 45,
            "products_limit": 100,
            "inventories_count": 1,
            "inventories_limit": 1,
            "products_remaining": 55,
            "inventories_remaining": 0
        }
    """
    from .constants import PLAN_LIMITS
    from .models import Product, Inventory

    # Obtener plan del usuario
    user_plan = user.plan if hasattr(user, 'plan') else 'free'
    limits = PLAN_LIMITS.get(user_plan, PLAN_LIMITS['free'])

    # Contar recursos actuales
    products_count = Product.objects.filter(
        inventory__owner=user,
        is_active=True
    ).count()

    inventories_count = Inventory.objects.filter(owner=user).count()

    # Obtener límites
    products_limit = limits['max_products']
    inventories_limit = limits['max_inventories']

    # Calcular recursos restantes
    products_remaining = -1 if products_limit == -1 else max(0, products_limit - products_count)
    inventories_remaining = -1 if inventories_limit == -1 else max(0, inventories_limit - inventories_count)

    return {
        'plan': user_plan,
        'plan_description': limits.get('description', ''),
        'products_count': products_count,
        'products_limit': products_limit if products_limit != -1 else 'unlimited',
        'products_remaining': products_remaining if products_remaining != -1 else 'unlimited',
        'inventories_count': inventories_count,
        'inventories_limit': inventories_limit if inventories_limit != -1 else 'unlimited',
        'inventories_remaining': inventories_remaining if inventories_remaining != -1 else 'unlimited',
    }

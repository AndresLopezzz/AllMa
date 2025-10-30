from rest_framework import serializers
from .models import BusinessTemplate, Inventory, Product


class BusinessTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer para BusinessTemplate (Plantillas de negocio).

    Expone las plantillas predefinidas con sus campos personalizados (custom_fields).
    Los custom_fields deben seguir esta estructura:
    [
        {
            "name": "talla",
            "type": "text|number|select|checkbox",
            "required": true|false,
            "options": ["S", "M", "L"]  # Solo para type="select"
        }
    ]
    """
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)

    class Meta:
        model = BusinessTemplate
        fields = [
            'id',
            'name',
            'description',
            'custom_fields',
            'created_by',
            'created_by_name',
            'created_by_email',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def validate_custom_fields(self, value):
        """
        Valida que custom_fields tenga la estructura correcta.

        Django REST Framework llama automáticamente a validate_<nombre_campo>
        para validar campos específicos.
        """
        if not isinstance(value, list):
            raise serializers.ValidationError("custom_fields debe ser una lista")

        for field in value:
            if not isinstance(field, dict):
                raise serializers.ValidationError("Cada campo debe ser un objeto")

            # Validar campos requeridos
            if 'name' not in field or 'type' not in field:
                raise serializers.ValidationError("Cada campo debe tener 'name' y 'type'")

            # Validar tipo
            valid_types = ['text', 'number', 'select', 'checkbox', 'textarea', 'date']
            if field['type'] not in valid_types:
                raise serializers.ValidationError(
                    f"Tipo '{field['type']}' no válido. Tipos permitidos: {', '.join(valid_types)}"
                )

            # Si es select, debe tener options
            if field['type'] == 'select' and 'options' not in field:
                raise serializers.ValidationError("Los campos de tipo 'select' deben tener 'options'")

            # Validar que required sea booleano
            if 'required' in field and not isinstance(field['required'], bool):
                raise serializers.ValidationError("El campo 'required' debe ser true o false")

        return value


class InventoryListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar inventarios (sin productos).
    Se usa en listas para no cargar demasiada data.
    """
    owner_name = serializers.CharField(source='owner.name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)

    class Meta:
        model = Inventory
        fields = [
            'id',
            'name',
            'owner',
            'owner_name',
            'template',
            'template_name',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']


class InventoryDetailSerializer(serializers.ModelSerializer):
    """
    Serializer completo para ver/editar un inventario específico.
    Incluye la plantilla completa con sus custom_fields.
    """
    owner_name = serializers.CharField(source='owner.name', read_only=True)
    template_data = BusinessTemplateSerializer(source='template', read_only=True)

    class Meta:
        model = Inventory
        fields = [
            'id',
            'name',
            'owner',
            'owner_name',
            'template',
            'template_data',
            'custom_template_fields',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer para productos.
    Incluye campos calculados como stock_status.
    """
    stock_status = serializers.CharField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    is_out_of_stock = serializers.BooleanField(read_only=True)
    inventory_name = serializers.CharField(source='inventory.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'sku',
            'description',
            'quantity',
            'price',
            'category',
            'inventory',
            'inventory_name',
            'custom_data',
            'low_stock_threshold',
            'stock_status',
            'is_low_stock',
            'is_out_of_stock',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_sku(self, value):
        """
        Valida que el SKU sea único dentro del inventario.
        """
        # Obtener el inventario del contexto (se pasa desde la vista)
        inventory = self.initial_data.get('inventory')

        # Si estamos actualizando, excluir el producto actual
        instance = self.instance

        # Query para verificar unicidad
        query = Product.objects.filter(sku=value, inventory_id=inventory)
        if instance:
            query = query.exclude(pk=instance.pk)

        if query.exists():
            raise serializers.ValidationError(
                "Ya existe un producto con este SKU en este inventario"
            )

        return value

    def validate_quantity(self, value):
        """
        Valida que la cantidad sea >= 0
        """
        if value < 0:
            raise serializers.ValidationError("La cantidad no puede ser negativa")
        return value

    def validate_price(self, value):
        """
        Valida que el precio sea >= 0
        """
        if value < 0:
            raise serializers.ValidationError("El precio no puede ser negativo")
        return value

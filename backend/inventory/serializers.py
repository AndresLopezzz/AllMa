from rest_framework import serializers
from .models import BusinessTemplate, Inventory, Product
from .utils import get_effective_template, validate_custom_fields_structure
from .constants import ERROR_MESSAGES


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
    Serializer ligero para listas de inventarios.
    Se usa en listas para no cargar demasiada data.
    """
    owner_name = serializers.CharField(source='owner.name', read_only=True)
    template_name = serializers.SerializerMethodField(read_only=True)

    def get_template_name(self, obj):
        """Devuelve el nombre de la plantilla o None si no hay plantilla"""
        return obj.template.name if obj.template else None

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
    template_data = serializers.SerializerMethodField(read_only=True)
    custom_fields = serializers.SerializerMethodField(read_only=True)

    def get_template_data(self, obj):
        """Devuelve los datos de la plantilla o None si no hay plantilla"""
        if obj.template:
            serializer = BusinessTemplateSerializer(obj.template)
            return serializer.data
        return None

    def get_custom_fields(self, obj):
        """
        Devuelve los custom_fields efectivos del inventario.
        Usa get_effective_template para priorizar custom_template_fields.
        """
        return get_effective_template(obj)

    class Meta:
        model = Inventory
        fields = [
            'id',
            'name',
            'owner',
            'owner_name',
            'template',
            'template_data',
            'custom_fields',
            'custom_template_fields',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer para productos.
    Incluye campos calculados como stock_status y template_info.
    Valida custom_data contra los custom_fields del template del inventario.
    """
    stock_status = serializers.CharField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    is_out_of_stock = serializers.BooleanField(read_only=True)
    inventory_name = serializers.CharField(source='inventory.name', read_only=True)
    template_info = serializers.SerializerMethodField(read_only=True)
    image_url = serializers.SerializerMethodField(read_only=True)
    image_versions = serializers.SerializerMethodField(read_only=True)

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
            'image',
            'image_url',
            'image_versions',
            'inventory',
            'inventory_name',
            'custom_data',
            'template_info',
            'low_stock_threshold',
            'stock_status',
            'is_low_stock',
            'is_out_of_stock',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_template_info(self, obj):
        """
        Devuelve los custom_fields efectivos del inventario.
        Usa get_effective_template para priorizar custom_template_fields.
        """
        return get_effective_template(obj.inventory)

    def get_image_url(self, obj):
        """
        Devuelve la URL optimizada de la imagen de Cloudinary.
        Aplica transformaciones automáticas:
        - f_auto: Formato automático (WebP, AVIF según soporte del navegador)
        - q_auto: Calidad automática optimizada
        - w_800: Ancho máximo de 800px (puedes ajustarlo)
        Si no hay imagen, devuelve None.
        """
        if obj.image:
            # Cloudinary permite transformaciones en la URL
            # Formato: .../upload/transformaciones/nombre.jpg
            url = obj.image.url

            # Insertar transformaciones después de /upload/
            if '/upload/' in url:
                # Transformaciones: formato auto, calidad auto, ancho máximo 800px
                transformations = 'f_auto,q_auto,w_800/'
                url = url.replace('/upload/', f'/upload/{transformations}')

            return url
        return None

    def get_image_versions(self, obj):
        """
        Devuelve múltiples versiones optimizadas de la imagen:
        - thumbnail: 200x200px (para listas/cards)
        - medium: 800px ancho (para vistas detalle)
        - full: original optimizado (para zoom/lightbox)

        Todas usan f_auto (WebP/AVIF) y q_auto para máxima optimización.
        """
        if not obj.image:
            return None

        base_url = obj.image.url

        if '/upload/' not in base_url:
            return None

        versions = {
            'thumbnail': base_url.replace('/upload/', '/upload/f_auto,q_auto,w_200,h_200,c_fill/'),
            'medium': base_url.replace('/upload/', '/upload/f_auto,q_auto,w_800,c_limit/'),
            'full': base_url.replace('/upload/', '/upload/f_auto,q_auto:best/')
        }

        return versions

    def create(self, validated_data):
        """
        Override create to attach user from request context for movement tracking.
        Ensure is_active is True for new products.
        """
        product = Product(**validated_data)
        product.is_active = True  # Ensure new products are active
        # Get user from context if available
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            product._performed_by = request.user
        product.save()
        return product

    def update(self, instance, validated_data):
        """
        Override update to attach user from request context for movement tracking.
        """
        # Get user from context if available
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            instance._performed_by = request.user

        # Update fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

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
        Valida que la cantidad sea mayor o igual a 0.
        """
        if value < 0:
            raise serializers.ValidationError(
                ERROR_MESSAGES['quantity_negative']
            )
        return value

    def validate_price(self, value):
        """
        Valida que el precio sea mayor a 0.
        """
        if value <= 0:
            raise serializers.ValidationError(
                ERROR_MESSAGES['price_invalid']
            )
        return value

    def validate_custom_data(self, value):
        """
        Valida que custom_data cumpla con la estructura definida en
        template.custom_fields del inventario.
        """
        if not value:
            return value

        # Obtener el inventario
        inventory_id = self.initial_data.get('inventory')
        if not inventory_id:
            raise serializers.ValidationError(
                "Debe especificar un inventario para validar custom_data"
            )

        try:
            inventory = Inventory.objects.select_related('template').get(id=inventory_id)
        except Inventory.DoesNotExist:
            raise serializers.ValidationError("El inventario especificado no existe")

        # Obtener los custom_fields efectivos (prioriza custom_template_fields)
        template_fields = get_effective_template(inventory)

        # Si el template no tiene custom_fields, pero se envían datos, es un error
        if not template_fields and value:
            raise serializers.ValidationError(
                "Este inventario no acepta campos personalizados"
            )

        # template_fields puede ser dict o list
        if isinstance(template_fields, dict):
            # Formato dict: {"campo": {"type": "text", "required": true}}
            for field_name, field_def in template_fields.items():
                field_type = field_def.get('type')
                field_required = field_def.get('required', False)

                # Verificar si el campo requerido está presente
                if field_required and field_name not in value:
                    raise serializers.ValidationError(
                        f"El campo '{field_name}' es requerido según el template"
                    )

                # Si el campo está presente, validar su tipo
                if field_name in value:
                    field_value = value[field_name]

                    # Validar según el tipo
                    if field_type == 'number':
                        if not isinstance(field_value, (int, float)):
                            try:
                                float(field_value)
                            except (ValueError, TypeError):
                                raise serializers.ValidationError(
                                    f"El campo '{field_name}' debe ser un número"
                                )

                    elif field_type == 'checkbox':
                        if not isinstance(field_value, bool):
                            raise serializers.ValidationError(
                                f"El campo '{field_name}' debe ser true o false"
                            )

                    elif field_type == 'select':
                        # Validar que el valor esté en las opciones
                        options = field_def.get('options', [])
                        if field_value not in options:
                            raise serializers.ValidationError(
                                f"El campo '{field_name}' debe ser uno de: {', '.join(options)}"
                            )
        elif isinstance(template_fields, list):
            # Formato list: [{"name": "campo", "type": "text", "required": true}]
            for field_def in template_fields:
                field_name = field_def.get('name')
                field_type = field_def.get('type')
                field_required = field_def.get('required', False)

                # Verificar si el campo requerido está presente
                if field_required and field_name not in value:
                    raise serializers.ValidationError(
                        f"El campo '{field_name}' es requerido según el template"
                    )

                # Si el campo está presente, validar su tipo
                if field_name in value:
                    field_value = value[field_name]

                    # Validar según el tipo
                    if field_type == 'number':
                        if not isinstance(field_value, (int, float)):
                            try:
                                float(field_value)
                            except (ValueError, TypeError):
                                raise serializers.ValidationError(
                                    f"El campo '{field_name}' debe ser un número"
                                )

                    elif field_type == 'checkbox':
                        if not isinstance(field_value, bool):
                            raise serializers.ValidationError(
                                f"El campo '{field_name}' debe ser true o false"
                            )

                    elif field_type == 'select':
                        # Validar que el valor esté en las opciones
                        options = field_def.get('options', [])
                        if field_value not in options:
                            raise serializers.ValidationError(
                                f"El campo '{field_name}' debe ser uno de: {', '.join(options)}"
                            )

        return value

    def validate(self, data):
        """
        Validación a nivel de objeto completo.
        Verifica que el inventario pertenezca al usuario (si no es admin).
        """
        inventory = data.get('inventory')
        request = self.context.get('request')

        if request and inventory:
            # Verificar que el inventario pertenece al usuario
            if not request.user.is_staff and inventory.owner != request.user:
                raise serializers.ValidationError(
                    "No puedes crear productos en un inventario que no te pertenece"
                )

        return data




class AlertSerializer(serializers.ModelSerializer):
    """
    Serializer para alertas de stock bajo.

    Incluye información crítica del producto, inventario y categoría.
    Calcula el ratio de criticidad: quantity / low_stock_threshold
    """
    inventory_name = serializers.CharField(source='inventory.name', read_only=True)
    inventory_id = serializers.IntegerField(source='inventory.id', read_only=True)
    owner_email = serializers.EmailField(source='inventory.owner.email', read_only=True)
    owner_name = serializers.CharField(source='inventory.owner.name', read_only=True)

    # Campo calculado: ratio de criticidad (más bajo = más crítico)
    criticality_ratio = serializers.SerializerMethodField(read_only=True)

    # URL de imagen optimizada
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'sku',
            'quantity',
            'low_stock_threshold',
            'price',
            'category',
            'image_url',
            'inventory_id',
            'inventory_name',
            'owner_email',
            'owner_name',
            'criticality_ratio',
            'alert_sent',
            'stock_status',
            'is_out_of_stock',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_criticality_ratio(self, obj):
        """
        Calcula el ratio de criticidad: quantity / low_stock_threshold

        Valores más bajos = más críticos
        - 0.0 = sin stock (crítico)
        - 0.5 = al 50% del umbral (medio)
        - 1.0 = justo en el umbral (bajo)
        """
        if obj.low_stock_threshold == 0:
            return 0.0
        return round(obj.quantity / obj.low_stock_threshold, 2)

    def get_image_url(self, obj):
        """
        Devuelve la URL de la imagen optimizada (thumbnail 200x200).
        """
        if obj.image:
            url = obj.image.url
            if '/upload/' in url:
                return url.replace('/upload/', '/upload/f_auto,q_auto,w_200,h_200,c_fill/')
        return None

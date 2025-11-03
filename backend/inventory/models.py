from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
from cloudinary.models import CloudinaryField


class BusinessTemplate(models.Model):
    """
    Plantilla de negocio - Define qué campos personalizados necesita cada tipo de negocio.

    Ejemplo para Ferretería:
    custom_fields = {
        "marca": {"type": "text", "required": true},
        "material": {"type": "text", "required": false},
        "medida": {"type": "text", "required": true}
    }
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nombre de la plantilla (ej: Ferretería, Ropa, Restaurante)"
    )
    description = models.TextField(
        blank=True,
        help_text="Descripción de qué tipo de negocio es esta plantilla"
    )
    custom_fields = models.JSONField(
        default=dict,
        blank=True,
        help_text="Estructura de campos personalizados que necesita este tipo de negocio"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_templates',
        help_text="Usuario que creó esta plantilla"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Si está activa, los usuarios pueden usarla"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Plantilla de Negocio"
        verbose_name_plural = "Plantillas de Negocio"
        ordering = ['name']

    def __str__(self):
        return self.name


class Inventory(models.Model):
    """
    Inventario - Una instancia específica de un negocio de un usuario.

    Por ejemplo: "Ferretería El Tornillo - Bodega Principal"
    """
    name = models.CharField(
        max_length=200,
        help_text="Nombre del inventario (ej: Bodega Principal, Tienda Centro)"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inventories',
        help_text="Usuario dueño de este inventario"
    )
    template = models.ForeignKey(
        BusinessTemplate,
        on_delete=models.PROTECT,
        related_name='inventories',
        help_text="Plantilla de negocio que usa este inventario"
    )
    custom_template_fields = models.JSONField(
        default=dict,
        blank=True,
        help_text="Personalización adicional de los campos de la plantilla (opcional)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Inventario"
        verbose_name_plural = "Inventarios"
        ordering = ['-created_at']
        # Un usuario no puede tener dos inventarios con el mismo nombre
        unique_together = ['owner', 'name']

    def __str__(self):
        return f"{self.name} ({self.owner.email})"


class Product(models.Model):
    """
    Producto - Artículo dentro de un inventario.

    Incluye campos estándar (nombre, precio, cantidad) + campos personalizados
    según la plantilla del inventario.
    """
    # Campos estándar
    name = models.CharField(
        max_length=200,
        help_text="Nombre del producto"
    )
    sku = models.CharField(
        max_length=100,
        help_text="Código único del producto (Stock Keeping Unit)"
    )
    description = models.TextField(
        blank=True,
        help_text="Descripción detallada del producto"
    )

    # Datos numéricos
    quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Cantidad disponible en stock"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Precio del producto"
    )
    low_stock_threshold = models.IntegerField(
        default=10,
        help_text="Cantidad mínima antes de alertar stock bajo"
    )

    # Categorización
    category = models.CharField(
        max_length=100,
        blank=True,
        help_text="Categoría del producto (ej: Herramientas, Pinturas)"
    )

    # Imagen del producto
    image = CloudinaryField(
        'image',
        blank=True,
        null=True,
        help_text="Imagen del producto almacenada en Cloudinary"
    )

    # Relación con inventario
    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name='products',
        help_text="Inventario al que pertenece este producto"
    )

    # Campos personalizados según la plantilla
    custom_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Datos personalizados según la plantilla del inventario (ej: marca, talla, color)"
    )

    # Estado
    is_active = models.BooleanField(
        default=True,
        help_text="Si es False, el producto está eliminado (soft delete)"
    )

    # Alertas
    alert_sent = models.BooleanField(
        default=False,
        help_text="Indica si ya se envió una alerta de stock bajo para este producto"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['-created_at']
        # El SKU debe ser único dentro de cada inventario
        unique_together = ['inventory', 'sku']

    def __str__(self):
        return f"{self.name} (SKU: {self.sku})"

    @property
    def is_low_stock(self):
        """Indica si el producto tiene stock bajo"""
        return self.quantity <= self.low_stock_threshold

    @property
    def is_out_of_stock(self):
        """Indica si el producto no tiene stock"""
        return self.quantity == 0

    @property
    def stock_status(self):
        """Retorna el estado del stock en texto"""
        if self.quantity == 0:
            return "Sin stock"
        elif self.is_low_stock:
            return "Stock bajo"
        else:
            return "En stock"


class Movement(models.Model):
    """
    Movimiento de inventario - Registra cada cambio en el stock de un producto.

    Permite mantener un historial completo de entradas, salidas y ajustes
    de inventario, incluyendo quién realizó cada movimiento y por qué.
    """
    MOVEMENT_TYPES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='movements',
        help_text="Producto al que pertenece este movimiento"
    )

    movement_type = models.CharField(
        max_length=10,
        choices=MOVEMENT_TYPES,
        help_text="Tipo de movimiento realizado"
    )

    quantity = models.IntegerField(
        help_text="Cantidad del movimiento (positivo para entradas, negativo para salidas)"
    )

    quantity_before = models.IntegerField(
        help_text="Cantidad antes del movimiento"
    )

    quantity_after = models.IntegerField(
        help_text="Cantidad después del movimiento"
    )

    reason = models.TextField(
        blank=True,
        help_text="Motivo o descripción del movimiento"
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='inventory_movements',
        help_text="Usuario que realizó el movimiento"
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora del movimiento"
    )

    class Meta:
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['product', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.get_movement_type_display()}: {self.product.name} ({self.quantity:+d}) - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

from django.contrib import admin
from django.utils.html import format_html
from .models import BusinessTemplate, Inventory, Product, Movement


class BusinessTemplateAdmin(admin.ModelAdmin):
    """
    Configuración del admin para BusinessTemplate
    """
    list_display = ('name', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Campos Personalizados', {
            'fields': ('custom_fields',),
            'description': 'Define los campos personalizados en formato JSON. Ejemplo: {"marca": {"type": "text", "required": true}}'
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class InventoryAdmin(admin.ModelAdmin):
    """
    Configuración del admin para Inventory
    """
    list_display = ('name', 'owner', 'template', 'created_at')
    list_filter = ('template', 'created_at')
    search_fields = ('name', 'owner__email')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'owner', 'template')
        }),
        ('Personalización', {
            'fields': ('custom_template_fields',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class ProductAdmin(admin.ModelAdmin):
    """
    Configuración del admin para Product
    """
    list_display = ('name', 'sku', 'inventory', 'quantity', 'price', 'get_stock_status', 'category')
    list_filter = ('inventory', 'category', 'created_at')
    search_fields = ('name', 'sku', 'description')
    readonly_fields = ('created_at', 'updated_at', 'get_stock_status')

    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'sku', 'description', 'inventory', 'category')
        }),
        ('Inventario y Precio', {
            'fields': ('quantity', 'price', 'low_stock_threshold', 'get_stock_status')
        }),
        ('Datos Personalizados', {
            'fields': ('custom_data',),
            'classes': ('collapse',),
            'description': 'Campos personalizados según la plantilla del inventario'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_stock_status(self, obj):
        """Muestra el estado del stock con colores"""
        status = obj.stock_status
        colors = {
            'Sin stock': 'red',
            'Stock bajo': 'orange',
            'En stock': 'green'
        }
        color = colors.get(status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            status
        )

    get_stock_status.short_description = 'Estado Stock'

    def save_model(self, request, obj, form, change):
        """
        Sobrescribe save_model para capturar el usuario que hace cambios.
        Esto permite que los signals sepan quién realizó el movimiento.
        """
        # Asignar el usuario actual al objeto para que el signal lo capture
        obj._performed_by = request.user
        super().save_model(request, obj, form, change)


class MovementAdmin(admin.ModelAdmin):
    """
    Configuración del admin para Movement
    """
    list_display = ('product', 'movement_type', 'quantity', 'quantity_before', 'quantity_after', 'performed_by', 'timestamp')
    list_filter = ('movement_type', 'timestamp', 'product__inventory')
    search_fields = ('product__name', 'product__sku', 'reason', 'performed_by__email')
    readonly_fields = ('product', 'movement_type', 'quantity', 'quantity_before', 'quantity_after', 'reason', 'performed_by', 'timestamp')

    fieldsets = (
        ('Información del Movimiento', {
            'fields': ('product', 'movement_type', 'quantity')
        }),
        ('Detalles del Cambio', {
            'fields': ('quantity_before', 'quantity_after', 'reason')
        }),
        ('Auditoría', {
            'fields': ('performed_by', 'timestamp')
        }),
    )

    def has_add_permission(self, request):
        """No permitir agregar movimientos manualmente"""
        return False

    def has_delete_permission(self, request, obj=None):
        """No permitir eliminar movimientos (auditoría)"""
        return False

    def has_change_permission(self, request, obj=None):
        """No permitir editar movimientos (auditoría)"""
        return False


# Registro tradicional (más compatible)
admin.site.register(BusinessTemplate, BusinessTemplateAdmin)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Movement, MovementAdmin)

from django.contrib import admin
from django.utils.html import format_html
from .models import BusinessTemplate, Inventory, Product


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


# Registro tradicional (más compatible)
admin.site.register(BusinessTemplate, BusinessTemplateAdmin)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(Product, ProductAdmin)

from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    exclude = ('username', 'first_name', 'last_name')  # Excluye estos campos del form
    fieldsets = (
        (None, {'fields': ('email', 'name', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Additional Info', {'fields': ('role', 'plan')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'role', 'plan', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'name', 'role', 'plan', 'is_active')
    search_fields = ('email', 'name')
    ordering = ('email',)

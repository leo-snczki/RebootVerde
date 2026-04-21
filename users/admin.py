from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserPoints

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'nif', 'is_staff')

    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('nif',)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Adicionais', {'fields': ('nif',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserPoints)

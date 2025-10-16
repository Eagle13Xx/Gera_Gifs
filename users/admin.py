# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    # Fieldsets controlam o layout da página de edição do usuário.
    fieldsets = UserAdmin.fieldsets + (
        # Criamos uma nova seção no formulário chamada 'Informações Adicionais'
        ('Informações Adicionais', {
            'fields': ('cellphone', 'taxId'),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Adicionais', {
            'fields': ('cellphone', 'taxId'),
        }),
    )

admin.site.register(User, CustomUserAdmin)
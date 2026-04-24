from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, TipoUsuario

@admin.register(TipoUsuario)
class TipoUsuarioAdmin(admin.ModelAdmin):
    list_display = ("id", "perfil")
    search_fields = ("perfil",)

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario

    list_display = ("id", "username", "nome", "email", "tipo_usuario", "is_staff", "is_active")
    search_fields = ("username", "nome", "email")
    list_filter = ("tipo_usuario", "is_staff", "is_active")

    fieldsets = UserAdmin.fieldsets + (
        ("Dados do EduMind", {
            "fields": ("nome", "tipo_usuario", "criado_em")
        }),
    )

    readonly_fields = ("criado_em",)
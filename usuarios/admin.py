from django.contrib import admin
from .models import Usuario, Estudante, Administrador


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "email", "tipo_usuario", "is_active")
    list_display_links = ("id", "nome")
    search_fields = ("nome", "email")
    list_filter = ("tipo_usuario", "is_active")
    ordering = ("nome",)
    list_per_page = 20

    fieldsets = (
        ("Informações principais", {
            "fields": ("nome", "email", "username", "password", "tipo_usuario")
        }),
        ("Status", {
            "fields": ("is_active", "is_staff", "is_superuser")
        }),
        ("Datas e permissões", {
            "fields": ("last_login", "date_joined", "criado_em", "groups", "user_permissions"),
            "classes": ("collapse",)
        }),
    )

    readonly_fields = ("last_login", "date_joined", "criado_em")


@admin.register(Estudante)
class EstudanteAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "semestre")
    list_display_links = ("id", "usuario")
    search_fields = ("usuario__nome", "usuario__email")
    ordering = ("usuario__nome",)
    list_per_page = 20

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "usuario":
            kwargs["queryset"] = Usuario.objects.filter(tipo_usuario="estudante")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario")
    list_display_links = ("id", "usuario")
    search_fields = ("usuario__nome", "usuario__email")
    ordering = ("usuario__nome",)
    list_per_page = 20

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "usuario":
            kwargs["queryset"] = Usuario.objects.filter(tipo_usuario="administrador")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
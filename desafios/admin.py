from django.contrib import admin
from .models import Desafio

@admin.register(Desafio)
class DesafioAdmin(admin.ModelAdmin):
    list_display = ("id", "titulo", "tipo_prova", "nivel", "ordem", "ativo")
    list_filter = ("tipo_prova", "ativo")
    search_fields = ("titulo",)
    filter_horizontal = ("questoes",)
    ordering = ("tipo_prova", "ordem")
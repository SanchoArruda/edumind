from django.contrib import admin

from .models import Quiz, Questao, Alternativa, Tentativa


class AlternativaInline(admin.TabularInline):
    model = Alternativa
    extra = 4


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("id", "titulo", "disciplina")
    search_fields = ("titulo", "disciplina__nome")
    list_filter = ("disciplina",)
    filter_horizontal = ("questoes",)
    ordering = ("titulo",)


@admin.register(Questao)
class QuestaoAdmin(admin.ModelAdmin):
    list_display = ("id", "disciplina", "enunciado_resumido")
    search_fields = ("enunciado", "disciplina__nome")
    list_filter = ("disciplina",)
    inlines = [AlternativaInline]

    def enunciado_resumido(self, obj):
        return obj.enunciado[:60] + "..." if len(obj.enunciado) > 60 else obj.enunciado

    enunciado_resumido.short_description = "Enunciado"


@admin.register(Alternativa)
class AlternativaAdmin(admin.ModelAdmin):
    list_display = ("id", "questao", "letra", "texto", "correta")
    search_fields = ("texto", "questao__enunciado")
    list_filter = ("correta", "letra")


@admin.register(Tentativa)
class TentativaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "tipo_tentativa",
        "usuario",
        "quiz",
        "desafio",
        "pontuacao",
        "quantidade_acertos",
        "quantidade_erros",
        "percentual_acertos",
        "concluida",
        "aprovado",
        "data_tentativa",
    )
    search_fields = (
        "usuario__username",
        "usuario__nome",
        "quiz__titulo",
        "desafio__titulo",
    )
    list_filter = (
        "tipo_tentativa",
        "concluida",
        "aprovado",
        "data_tentativa",
    )
    ordering = ("-data_tentativa",)
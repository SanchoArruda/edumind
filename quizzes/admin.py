from django.contrib import admin

from .models import Quiz, Questao, Alternativa, TentativaQuiz


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


@admin.register(TentativaQuiz)
class TentativaQuizAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "usuario",
        "quiz",
        "pontuacao",
        "quantidade_acertos",
        "quantidade_erros",
        "percentual_acertos",
        "concluida",
        "data_tentativa",
    )
    search_fields = ("usuario__username", "usuario__nome", "quiz__titulo")
    list_filter = ("concluida", "quiz", "data_tentativa")
    ordering = ("-data_tentativa",)
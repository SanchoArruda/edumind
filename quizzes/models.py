from django.conf import settings
from django.db import models

from disciplinas.models import Disciplina


class Questao(models.Model):
    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.CASCADE,
        related_name="questoes"
    )
    enunciado = models.TextField()
    explicacao_resposta = models.TextField(blank=True)

    class Meta:
        verbose_name = "Questão"
        verbose_name_plural = "Questões"

    def __str__(self):
        return f"Questão {self.id} - {self.disciplina.nome}"


class Alternativa(models.Model):
    questao = models.ForeignKey(
        Questao,
        on_delete=models.CASCADE,
        related_name="alternativas"
    )
    letra = models.CharField(max_length=1)
    texto = models.CharField(max_length=255)
    correta = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Alternativa"
        verbose_name_plural = "Alternativas"
        ordering = ["questao", "letra"]

    def __str__(self):
        return f"{self.letra}) {self.texto}"


class Quiz(models.Model):
    TIPO_PROVA_CHOICES = [
        ("ENADE", "ENADE"),
        ("POSCOMP", "POSCOMP"),
    ]

    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.CASCADE,
        related_name="quizzes"
    )
    titulo = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    tipo_prova = models.CharField(
        max_length=10,
        choices=TIPO_PROVA_CHOICES,
        default="ENADE"
    )
    questoes = models.ManyToManyField(
        Questao,
        related_name="quizzes",
        blank=True
    )

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quizzes"
        ordering = ["titulo"]

    def __str__(self):
        return self.titulo


class TentativaQuiz(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tentativas"
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="tentativas"
    )
    data_tentativa = models.DateTimeField(auto_now_add=True)
    pontuacao = models.FloatField(default=0)
    quantidade_acertos = models.PositiveIntegerField(default=0)
    quantidade_erros = models.PositiveIntegerField(default=0)
    percentual_acertos = models.FloatField(default=0)
    desempenho_geral = models.CharField(max_length=100, blank=True)
    tempo_gasto = models.DurationField(null=True, blank=True)
    concluida = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Tentativa de Quiz"
        verbose_name_plural = "Tentativas de Quiz"
        ordering = ["-data_tentativa"]

    def __str__(self):
        return f"{self.usuario} - {self.quiz.titulo}"
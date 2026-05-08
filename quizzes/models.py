from django.conf import settings
from django.db import models

from disciplinas.models import Disciplina


class Questao(models.Model):
    NIVEL_DIFICULDADE_CHOICES = [
        ("FACIL", "Fácil"),
        ("MEDIA", "Média"),
        ("DIFICIL", "Difícil"),
    ]

    TIPO_PROVA_CHOICES = [
        ("ENADE", "ENADE"),
        ("POSCOMP", "POSCOMP"),
        ("AMBOS", "Ambos"),
    ]

    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.CASCADE,
        related_name="questoes"
    )
    enunciado = models.TextField()
    explicacao_resposta = models.TextField(blank=True)

    nivel_dificuldade = models.CharField(
        max_length=10,
        choices=NIVEL_DIFICULDADE_CHOICES,
        default="MEDIA"
    )

    tipo_prova = models.CharField(
        max_length=10,
        choices=TIPO_PROVA_CHOICES,
        default="AMBOS"
    )

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


class Tentativa(models.Model):
    TIPO_TENTATIVA_CHOICES = [
        ("QUIZ", "Quiz"),
        ("DESAFIO", "Desafio"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tentativas_genericas"
    )
    quiz = models.ForeignKey(
        "Quiz",
        on_delete=models.CASCADE,
        related_name="tentativas_genericas",
        null=True,
        blank=True
    )
    desafio = models.ForeignKey(
        "desafios.Desafio",
        on_delete=models.CASCADE,
        related_name="tentativas_genericas",
        null=True,
        blank=True
    )
    tipo_tentativa = models.CharField(
        max_length=10,
        choices=TIPO_TENTATIVA_CHOICES
    )
    data_tentativa = models.DateTimeField(auto_now_add=True)
    pontuacao = models.FloatField(default=0)
    quantidade_acertos = models.PositiveIntegerField(default=0)
    quantidade_erros = models.PositiveIntegerField(default=0)
    percentual_acertos = models.FloatField(default=0)
    desempenho_geral = models.CharField(max_length=100, blank=True)
    tempo_gasto = models.DurationField(null=True, blank=True)
    concluida = models.BooleanField(default=False)
    aprovado = models.BooleanField(default=False)
    respostas = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Tentativa"
        verbose_name_plural = "Tentativas"
        ordering = ["-data_tentativa"]

    def __str__(self):
        if self.tipo_tentativa == "QUIZ" and self.quiz:
            return f"{self.usuario} - Quiz: {self.quiz.titulo}"
        if self.tipo_tentativa == "DESAFIO" and self.desafio:
            return f"{self.usuario} - Desafio: {self.desafio.titulo}"
        return f"{self.usuario} - Tentativa {self.id}"
    
    @property
    def tempo_formatado(self):
        if not self.tempo_gasto:
            return "Não registrado"

        total_segundos = int(self.tempo_gasto.total_seconds())

        minutos = total_segundos // 60
        segundos = total_segundos % 60

        if minutos > 0 and segundos > 0:
            return f"{minutos} min e {segundos} seg"

        if minutos > 0:
            return f"{minutos} min"

        return f"{segundos} seg"
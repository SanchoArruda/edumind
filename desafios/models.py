from django.db import models
from quizzes.models import Questao


class Desafio(models.Model):
    TIPO_PROVA_CHOICES = [
        ("ENADE", "ENADE"),
        ("POSCOMP", "POSCOMP"),
    ]

    NIVEL_CHOICES = [
        (1, "Fácil"),
        (2, "Médio"),
        (3, "Difícil"),
    ]

    titulo = models.CharField(max_length=150)
    tipo_prova = models.CharField(max_length=10, choices=TIPO_PROVA_CHOICES)

    nivel = models.PositiveIntegerField(
        choices=NIVEL_CHOICES,
        default=1
    )

    ordem = models.PositiveIntegerField(default=1)
    quantidade_questoes = models.PositiveIntegerField()
    tempo_total_segundos = models.PositiveIntegerField()
    ativo = models.BooleanField(default=True)

    questoes = models.ManyToManyField(
        Questao,
        related_name="desafios",
        blank=True
    )

    class Meta:
        verbose_name = "Desafio"
        verbose_name_plural = "Desafios"
        ordering = ["tipo_prova", "ordem"]
        constraints = [
            models.UniqueConstraint(
                fields=["tipo_prova", "ordem"],
                name="unique_desafio_tipo_prova_ordem"
            )
        ]

    @property
    def tempo_formatado(self):
        minutos = self.tempo_total_segundos // 60
        segundos = self.tempo_total_segundos % 60

        if minutos > 0 and segundos > 0:
            return f"{minutos} min e {segundos} seg"

        if minutos > 0:
            return f"{minutos} min"

        return f"{segundos} seg"

    def __str__(self):
        return f"{self.titulo} ({self.tipo_prova})"
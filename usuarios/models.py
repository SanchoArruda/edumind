from django.db import models
from django.contrib.auth.models import AbstractUser


class TipoUsuario(models.Model):
    perfil = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Tipo de Usuário"
        verbose_name_plural = "Tipos de Usuário"

    def __str__(self):
        return self.perfil


class Usuario(AbstractUser):
    tipo_usuario = models.ForeignKey(
        TipoUsuario,
        on_delete=models.PROTECT,
        related_name="usuarios",
        null=True,
        blank=True
    )

    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self):
        return self.nome or self.username
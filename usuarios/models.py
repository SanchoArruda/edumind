from django.db import models
from django.contrib.auth.models import AbstractUser
#lançar um erro de validação quando alguma regra sistema for quebrada.
from django.core.exceptions import ValidationError


class Usuario(AbstractUser):
    TIPO_USUARIO_CHOICES = [
        ("estudante", "Estudante"),
        ("administrador", "Administrador"),
    ]

    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self):
        return self.nome or self.username


class Estudante(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name="perfil_estudante"
    )
    semestre = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Estudante"
        verbose_name_plural = "Estudantes"

    def __str__(self):
        return self.usuario.nome or self.usuario.username

    #Esse método verifica se o objeto está válido antes de salvar.
    def clean(self):
        if self.usuario.tipo_usuario != "estudante":
            raise ValidationError("Somente usuários do tipo estudante podem ser vinculados a Estudante.")
        
    # Salva o objeto , passando pelas validacoes, se estiver tudo certo, salva.
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Administrador(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name="perfil_administrador"
    )

    class Meta:
        verbose_name = "Administrador"
        verbose_name_plural = "Administradores"

    def __str__(self):
        return self.usuario.nome or self.usuario.username

    #Esse método verifica se o objeto está válido antes de salvar.
    def clean(self):
        if self.usuario.tipo_usuario != "administrador":
            raise ValidationError("Somente usuários do tipo administrador podem ser vinculados a Administrador.")
   
    # Salva o objeto , passando pelas validacoes, se estiver tudo certo, salva.
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
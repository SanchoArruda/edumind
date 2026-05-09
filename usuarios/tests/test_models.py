from django.db import IntegrityError
from django.test import TestCase

from usuarios.models import Usuario, TipoUsuario


class TipoUsuarioModelTest(TestCase):
    def test_criar_tipo_usuario(self):
        tipo = TipoUsuario.objects.create(perfil="Estudante")

        self.assertEqual(tipo.perfil, "Estudante")
        self.assertEqual(str(tipo), "Estudante")

    def test_tipo_usuario_perfil_unico(self):
        TipoUsuario.objects.create(perfil="Administrador")

        with self.assertRaises(IntegrityError):
            TipoUsuario.objects.create(perfil="Administrador")


class UsuarioModelTest(TestCase):
    def setUp(self):
        self.tipo_estudante = TipoUsuario.objects.create(perfil="Estudante")
        self.tipo_admin = TipoUsuario.objects.create(perfil="Administrador")

    def test_criar_usuario_estudante(self):
        usuario = Usuario.objects.create_user(
            username="estudante",
            nome="Estudante Teste",
            email="estudante@email.com",
            password="123456",
            tipo_usuario=self.tipo_estudante,
        )

        self.assertEqual(usuario.username, "estudante")
        self.assertEqual(usuario.nome, "Estudante Teste")
        self.assertEqual(usuario.email, "estudante@email.com")
        self.assertEqual(usuario.tipo_usuario.perfil, "Estudante")
        self.assertTrue(usuario.check_password("123456"))
        self.assertEqual(str(usuario), "Estudante Teste")

    def test_criar_usuario_admin(self):
        usuario = Usuario.objects.create_user(
            username="admin",
            nome="Admin Teste",
            email="admin@email.com",
            password="123456",
            tipo_usuario=self.tipo_admin,
        )

        self.assertEqual(usuario.tipo_usuario.perfil, "Administrador")
        self.assertEqual(str(usuario), "Admin Teste")

    def test_str_retorna_username_quando_nome_vazio(self):
        usuario = Usuario.objects.create_user(
            username="semnome",
            nome="",
            email="semnome@email.com",
            password="123456",
            tipo_usuario=self.tipo_estudante,
        )

        self.assertEqual(str(usuario), "semnome")
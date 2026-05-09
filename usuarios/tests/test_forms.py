from django.test import TestCase

from usuarios.forms import CadastroEstudanteForm, LoginForm, UsuarioAdminForm
from usuarios.models import Usuario, TipoUsuario


class CadastroEstudanteFormTest(TestCase):
    def test_formulario_cadastro_valido(self):
        form = CadastroEstudanteForm(data={
            "nome": "Estudante Teste",
            "username": "estudante",
            "email": "estudante@email.com",
            "password": "123456",
            "confirmar_password": "123456",
        })

        self.assertTrue(form.is_valid())

    def test_formulario_cadastro_senhas_diferentes_invalido(self):
        form = CadastroEstudanteForm(data={
            "nome": "Estudante Teste",
            "username": "estudante",
            "email": "estudante@email.com",
            "password": "123456",
            "confirmar_password": "654321",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("As senhas não coincidem.", form.non_field_errors())

    def test_formulario_cadastro_email_duplicado_invalido(self):
        tipo = TipoUsuario.objects.create(perfil="Estudante")

        Usuario.objects.create_user(
            username="existente",
            nome="Usuário Existente",
            email="existente@email.com",
            password="123456",
            tipo_usuario=tipo,
        )

        form = CadastroEstudanteForm(data={
            "nome": "Novo Estudante",
            "username": "novo",
            "email": "existente@email.com",
            "password": "123456",
            "confirmar_password": "123456",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_formulario_cadastro_username_duplicado_invalido(self):
        tipo = TipoUsuario.objects.create(perfil="Estudante")

        Usuario.objects.create_user(
            username="existente",
            nome="Usuário Existente",
            email="existente@email.com",
            password="123456",
            tipo_usuario=tipo,
        )

        form = CadastroEstudanteForm(data={
            "nome": "Novo Estudante",
            "username": "existente",
            "email": "novo@email.com",
            "password": "123456",
            "confirmar_password": "123456",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)


class LoginFormTest(TestCase):
    def test_login_form_campos_obrigatorios(self):
        form = LoginForm(request=None, data={})

        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
        self.assertIn("password", form.errors)


class UsuarioAdminFormTest(TestCase):
    def setUp(self):
        self.tipo_estudante = TipoUsuario.objects.create(perfil="Estudante")

        self.usuario = Usuario.objects.create_user(
            username="estudante",
            nome="Estudante Teste",
            email="estudante@email.com",
            password="123456",
            tipo_usuario=self.tipo_estudante,
        )

    def test_usuario_admin_form_valido(self):
        form = UsuarioAdminForm(
            data={
                "nome": "Estudante Atualizado",
                "username": "estudante_atualizado",
                "email": "atualizado@email.com",
                "is_active": "on",
            },
            instance=self.usuario,
        )

        self.assertTrue(form.is_valid())

    def test_usuario_admin_form_atualiza_usuario(self):
        form = UsuarioAdminForm(
            data={
                "nome": "Estudante Atualizado",
                "username": "estudante_atualizado",
                "email": "atualizado@email.com",
                "is_active": "on",
            },
            instance=self.usuario,
        )

        self.assertTrue(form.is_valid())

        usuario = form.save()

        self.assertEqual(usuario.nome, "Estudante Atualizado")
        self.assertEqual(usuario.username, "estudante_atualizado")
        self.assertEqual(usuario.email, "atualizado@email.com")
        self.assertTrue(usuario.is_active)
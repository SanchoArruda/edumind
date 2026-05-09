from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from disciplinas.models import Disciplina
from usuarios.models import TipoUsuario


User = get_user_model()


class DisciplinaViewTest(TestCase):

    def setUp(self):
        self.tipo_admin = TipoUsuario.objects.create(perfil="administrador")
        self.tipo_estudante = TipoUsuario.objects.create(perfil="estudante")

        self.admin = User.objects.create_user(
            username="admin",
            email="admin@email.com",
            password="123456",
            tipo_usuario=self.tipo_admin
        )

        self.estudante = User.objects.create_user(
            username="estudante",
            email="estudante@email.com",
            password="123456",
            tipo_usuario=self.tipo_estudante
        )

    def test_admin_deve_acessar_lista_de_disciplinas(self):
        self.client.login(username="admin", password="123456")

        response = self.client.get(
            reverse("disciplinas:admin_lista_disciplinas")
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "disciplinas/admin/admin_lista_disciplinas.html"
        )

    def test_estudante_nao_deve_acessar_lista_de_disciplinas(self):
        self.client.login(username="estudante", password="123456")

        response = self.client.get(
            reverse("disciplinas:admin_lista_disciplinas")
        )

        self.assertRedirects(response, reverse("login"))

    def test_usuario_nao_logado_deve_ser_redirecionado_ao_acessar_lista(self):
        response = self.client.get(
            reverse("disciplinas:admin_lista_disciplinas")
        )

        self.assertEqual(response.status_code, 302)

    def test_lista_deve_exibir_disciplinas_ordenadas_por_nome(self):
        Disciplina.objects.create(nome="Redes")
        Disciplina.objects.create(nome="Algoritmos")
        Disciplina.objects.create(nome="Banco de Dados")

        self.client.login(username="admin", password="123456")

        response = self.client.get(
            reverse("disciplinas:admin_lista_disciplinas")
        )

        disciplinas = list(response.context["disciplinas"])

        self.assertEqual(disciplinas[0].nome, "Algoritmos")
        self.assertEqual(disciplinas[1].nome, "Banco de Dados")
        self.assertEqual(disciplinas[2].nome, "Redes")
        self.assertEqual(response.context["total_disciplinas"], 3)

    def test_admin_deve_acessar_formulario_de_criacao(self):
        self.client.login(username="admin", password="123456")

        response = self.client.get(
            reverse("disciplinas:admin_criar_disciplina")
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "disciplinas/admin/admin_form_disciplina.html"
        )
        self.assertIn("form", response.context)
        self.assertEqual(response.context["titulo_pagina"], "Nova Disciplina")
        self.assertEqual(response.context["botao_submit"], "Cadastrar Disciplina")

    def test_admin_deve_criar_disciplina(self):
        self.client.login(username="admin", password="123456")

        response = self.client.post(
            reverse("disciplinas:admin_criar_disciplina"),
            data={
                "nome": "Banco de Dados"
            }
        )

        self.assertRedirects(
            response,
            reverse("disciplinas:admin_lista_disciplinas")
        )
        self.assertTrue(
            Disciplina.objects.filter(nome="Banco de Dados").exists()
        )

    def test_nao_deve_criar_disciplina_sem_nome(self):
        self.client.login(username="admin", password="123456")

        response = self.client.post(
            reverse("disciplinas:admin_criar_disciplina"),
            data={
                "nome": ""
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Disciplina.objects.exists())
        self.assertIn("form", response.context)
        self.assertTrue(response.context["form"].errors)

    def test_nao_deve_criar_disciplina_com_nome_duplicado(self):
        Disciplina.objects.create(nome="Banco de Dados")

        self.client.login(username="admin", password="123456")

        response = self.client.post(
            reverse("disciplinas:admin_criar_disciplina"),
            data={
                "nome": "banco de dados"
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Disciplina.objects.count(), 1)
        self.assertIn("form", response.context)
        self.assertIn("nome", response.context["form"].errors)

    def test_admin_deve_acessar_formulario_de_edicao(self):
        disciplina = Disciplina.objects.create(nome="Banco de Dados")

        self.client.login(username="admin", password="123456")

        response = self.client.get(
            reverse(
                "disciplinas:admin_editar_disciplina",
                args=[disciplina.id]
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "disciplinas/admin/admin_form_disciplina.html"
        )
        self.assertEqual(response.context["disciplina"], disciplina)
        self.assertEqual(response.context["titulo_pagina"], "Editar Disciplina")
        self.assertEqual(response.context["botao_submit"], "Salvar Alterações")

    def test_admin_deve_editar_disciplina(self):
        disciplina = Disciplina.objects.create(nome="Banco de Dados")

        self.client.login(username="admin", password="123456")

        response = self.client.post(
            reverse(
                "disciplinas:admin_editar_disciplina",
                args=[disciplina.id]
            ),
            data={
                "nome": "Estrutura de Dados"
            }
        )

        disciplina.refresh_from_db()

        self.assertRedirects(
            response,
            reverse("disciplinas:admin_lista_disciplinas")
        )
        self.assertEqual(disciplina.nome, "Estrutura de Dados")

    def test_nao_deve_editar_disciplina_para_nome_vazio(self):
        disciplina = Disciplina.objects.create(nome="Banco de Dados")

        self.client.login(username="admin", password="123456")

        response = self.client.post(
            reverse(
                "disciplinas:admin_editar_disciplina",
                args=[disciplina.id]
            ),
            data={
                "nome": ""
            }
        )

        disciplina.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(disciplina.nome, "Banco de Dados")
        self.assertIn("form", response.context)
        self.assertIn("nome", response.context["form"].errors)

    def test_nao_deve_editar_disciplina_para_nome_duplicado(self):
        Disciplina.objects.create(nome="Banco de Dados")
        disciplina = Disciplina.objects.create(nome="Redes")

        self.client.login(username="admin", password="123456")

        response = self.client.post(
            reverse(
                "disciplinas:admin_editar_disciplina",
                args=[disciplina.id]
            ),
            data={
                "nome": "Banco de Dados"
            }
        )

        disciplina.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(disciplina.nome, "Redes")
        self.assertIn("form", response.context)
        self.assertIn("nome", response.context["form"].errors)

    def test_admin_deve_excluir_disciplina(self):
        disciplina = Disciplina.objects.create(nome="Banco de Dados")

        self.client.login(username="admin", password="123456")

        response = self.client.post(
            reverse(
                "disciplinas:admin_excluir_disciplina",
                args=[disciplina.id]
            )
        )

        self.assertRedirects(
            response,
            reverse("disciplinas:admin_lista_disciplinas")
        )
        self.assertFalse(
            Disciplina.objects.filter(id=disciplina.id).exists()
        )

    def test_get_na_exclusao_nao_deve_excluir_disciplina(self):
        disciplina = Disciplina.objects.create(nome="Banco de Dados")

        self.client.login(username="admin", password="123456")

        response = self.client.get(
            reverse(
                "disciplinas:admin_excluir_disciplina",
                args=[disciplina.id]
            )
        )

        self.assertRedirects(
            response,
            reverse("disciplinas:admin_lista_disciplinas")
        )
        self.assertTrue(
            Disciplina.objects.filter(id=disciplina.id).exists()
        )

    def test_estudante_nao_deve_criar_disciplina(self):
        self.client.login(username="estudante", password="123456")

        response = self.client.post(
            reverse("disciplinas:admin_criar_disciplina"),
            data={
                "nome": "Banco de Dados"
            }
        )

        self.assertRedirects(response, reverse("login"))
        self.assertFalse(Disciplina.objects.exists())

    def test_estudante_nao_deve_editar_disciplina(self):
        disciplina = Disciplina.objects.create(nome="Banco de Dados")

        self.client.login(username="estudante", password="123456")

        response = self.client.post(
            reverse(
                "disciplinas:admin_editar_disciplina",
                args=[disciplina.id]
            ),
            data={
                "nome": "Redes"
            }
        )

        disciplina.refresh_from_db()

        self.assertRedirects(response, reverse("login"))
        self.assertEqual(disciplina.nome, "Banco de Dados")

    def test_estudante_nao_deve_excluir_disciplina(self):
        disciplina = Disciplina.objects.create(nome="Banco de Dados")

        self.client.login(username="estudante", password="123456")

        response = self.client.post(
            reverse(
                "disciplinas:admin_excluir_disciplina",
                args=[disciplina.id]
            )
        )

        self.assertRedirects(response, reverse("login"))
        self.assertTrue(
            Disciplina.objects.filter(id=disciplina.id).exists()
        )
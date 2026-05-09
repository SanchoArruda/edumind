from django.test import TestCase
from django.urls import reverse

from desafios.models import Desafio
from disciplinas.models import Disciplina
from quizzes.models import Quiz, Questao, Tentativa
from usuarios.models import Usuario, TipoUsuario


class UsuariosViewsTest(TestCase):
    def setUp(self):
        self.tipo_estudante = TipoUsuario.objects.create(perfil="Estudante")
        self.tipo_admin = TipoUsuario.objects.create(perfil="Administrador")

        self.estudante = Usuario.objects.create_user(
            username="estudante",
            nome="Estudante Teste",
            email="estudante@email.com",
            password="123456",
            tipo_usuario=self.tipo_estudante,
        )

        self.admin = Usuario.objects.create_user(
            username="admin",
            nome="Admin Teste",
            email="admin@email.com",
            password="123456",
            tipo_usuario=self.tipo_admin,
        )

    def test_pagina_cadastro_carrega(self):
        response = self.client.get(reverse("cadastro"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_cadastro_estudante_cria_usuario(self):
        response = self.client.post(
            reverse("cadastro"),
            {
                "nome": "Novo Estudante",
                "username": "novoestudante",
                "email": "novo@email.com",
                "password": "123456",
                "confirmar_password": "123456",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Usuario.objects.filter(username="novoestudante").exists()
        )

        usuario = Usuario.objects.get(username="novoestudante")

        self.assertEqual(usuario.tipo_usuario.perfil, "Estudante")

    def test_login_estudante_redireciona_para_dashboard_estudante(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "estudante",
                "password": "123456",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/usuarios/estudante-dashboard/")

    def test_login_admin_redireciona_para_dashboard_admin(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "admin",
                "password": "123456",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/usuarios/admin-dashboard/")

    def test_dashboard_estudante_exige_login(self):
        response = self.client.get(reverse("dashboard_estudante"))

        self.assertEqual(response.status_code, 302)

    def test_estudante_acessa_dashboard_estudante(self):
        self.client.login(username="estudante", password="123456")

        response = self.client.get(reverse("dashboard_estudante"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("total_quizzes_feitos", response.context)
        self.assertIn("taxa_acerto", response.context)
        self.assertIn("xp_total", response.context)
        self.assertIn("nivel_atual", response.context)

    def test_admin_nao_acessa_dashboard_estudante(self):
        self.client.login(username="admin", password="123456")

        response = self.client.get(reverse("dashboard_estudante"))

        self.assertEqual(response.status_code, 302)

    def test_admin_acessa_dashboard_admin(self):
        self.client.login(username="admin", password="123456")

        response = self.client.get(reverse("dashboard_admin"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("total_estudantes", response.context)
        self.assertIn("total_quizzes", response.context)
        self.assertIn("total_questoes", response.context)
        self.assertIn("total_desafios", response.context)
        self.assertIn("total_disciplinas", response.context)
        self.assertIn("total_tentativas", response.context)

    def test_estudante_nao_acessa_dashboard_admin(self):
        self.client.login(username="estudante", password="123456")

        response = self.client.get(reverse("dashboard_admin"))

        self.assertEqual(response.status_code, 302)

    def test_admin_acessa_lista_estudantes(self):
        self.client.login(username="admin", password="123456")

        response = self.client.get(reverse("admin_lista_estudantes"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Estudante Teste")
        self.assertIn("estudantes", response.context)
        self.assertIn("total_estudantes", response.context)

    def test_estudante_nao_acessa_lista_estudantes(self):
        self.client.login(username="estudante", password="123456")

        response = self.client.get(reverse("admin_lista_estudantes"))

        self.assertEqual(response.status_code, 302)

    def test_admin_edita_estudante(self):
        self.client.login(username="admin", password="123456")

        response = self.client.post(
            reverse("admin_editar_estudante", args=[self.estudante.id]),
            {
                "nome": "Estudante Editado",
                "username": "estudante_editado",
                "email": "editado@email.com",
                "is_active": "on",
            },
        )

        self.estudante.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.estudante.nome, "Estudante Editado")
        self.assertEqual(self.estudante.username, "estudante_editado")
        self.assertEqual(self.estudante.email, "editado@email.com")

    def test_admin_exclui_estudante(self):
        self.client.login(username="admin", password="123456")

        response = self.client.post(
            reverse("admin_excluir_estudante", args=[self.estudante.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Usuario.objects.filter(id=self.estudante.id).exists()
        )

    def test_meu_perfil_exige_login(self):
        response = self.client.get(reverse("meu_perfil"))

        self.assertEqual(response.status_code, 302)

    def test_estudante_acessa_meu_perfil(self):
        self.client.login(username="estudante", password="123456")

        response = self.client.get(reverse("meu_perfil"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["usuario_obj"], self.estudante)
        self.assertEqual(response.context["template_base"], "base/base_dashboard.html")

    def test_admin_acessa_meu_perfil_com_template_admin(self):
        self.client.login(username="admin", password="123456")

        response = self.client.get(reverse("meu_perfil"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["usuario_obj"], self.admin)
        self.assertEqual(response.context["template_base"], "base/base_admin.html")


    def test_cadastro_estudante_invalido_nao_cria_usuario(self):
        response = self.client.post(
            reverse("cadastro"),
            {
                "nome": "Estudante Inválido",
                "username": "invalido",
                "email": "invalido@email.com",
                "password": "123456",
                "confirmar_password": "654321",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Usuario.objects.filter(username="invalido").exists()
        )
        self.assertIn("form", response.context)

    def test_admin_acessa_form_editar_estudante_get(self):
        self.client.login(username="admin", password="123456")

        response = self.client.get(
            reverse("admin_editar_estudante", args=[self.estudante.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)
        self.assertEqual(response.context["usuario_obj"], self.estudante)
        self.assertEqual(response.context["titulo"], "Editar estudante")
        self.assertEqual(response.context["botao"], "Salvar alterações")

    def test_admin_acessa_confirmacao_excluir_estudante_get(self):
        self.client.login(username="admin", password="123456")

        response = self.client.get(
            reverse("admin_excluir_estudante", args=[self.estudante.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["usuario_obj"], self.estudante)

    def test_sair_redireciona_para_login(self):
        self.client.login(username="estudante", password="123456")

        response = self.client.get(reverse("logout"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))

    def test_estudante_acessa_perfil_estudante(self):
        self.client.login(username="estudante", password="123456")

        response = self.client.get(reverse("perfil_estudante"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("total_quizzes", response.context)
        self.assertIn("total_acertos", response.context)
        self.assertIn("total_erros", response.context)
        self.assertIn("total_questoes", response.context)
        self.assertIn("taxa_acerto", response.context)
        self.assertIn("xp_total", response.context)
        self.assertIn("tentativas", response.context)
        self.assertIn("tentativas_desafios", response.context)
        self.assertIn("total_desafios_concluidos", response.context)
        self.assertIn("melhor_estrelas_desafio", response.context)

    def test_admin_nao_acessa_perfil_estudante(self):
        self.client.login(username="admin", password="123456")

        response = self.client.get(reverse("perfil_estudante"))

        self.assertEqual(response.status_code, 302)

    def test_estudante_acessa_perfil_estudante_com_tentativas(self):
        disciplina = Disciplina.objects.create(nome="Algoritmo")

        quiz = Quiz.objects.create(
            disciplina=disciplina,
            titulo="Quiz de Algoritmo",
            tipo_prova="ENADE",
        )

        desafio_enade = Desafio.objects.create(
            titulo="Desafio ENADE",
            tipo_prova="ENADE",
            nivel=1,
            ordem=1,
            quantidade_questoes=2,
            tempo_total_segundos=600,
            ativo=True,
        )

        Tentativa.objects.create(
            usuario=self.estudante,
            quiz=quiz,
            tipo_tentativa="QUIZ",
            quantidade_acertos=3,
            quantidade_erros=1,
            percentual_acertos=75,
            pontuacao=15,
            concluida=True,
        )

        Tentativa.objects.create(
            usuario=self.estudante,
            desafio=desafio_enade,
            tipo_tentativa="DESAFIO",
            quantidade_acertos=2,
            quantidade_erros=0,
            percentual_acertos=100,
            pontuacao=5,
            concluida=True,
            aprovado=True,
        )

        self.client.login(username="estudante", password="123456")

        response = self.client.get(reverse("perfil_estudante"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_quizzes"], 1)
        self.assertEqual(response.context["total_acertos"], 3)
        self.assertEqual(response.context["total_erros"], 1)
        self.assertEqual(response.context["total_questoes"], 4)
        self.assertEqual(response.context["taxa_acerto"], 75)
        self.assertEqual(response.context["xp_total"], 15)
        self.assertEqual(response.context["total_desafios_concluidos"], 1)
        self.assertEqual(response.context["melhor_estrelas_desafio"], 5)
        self.assertEqual(response.context["desafios_enade_concluidos"], 1)
        self.assertEqual(response.context["desafios_poscomp_concluidos"], 0)

    def test_estudante_acessa_ranking_estudante(self):
        disciplina = Disciplina.objects.create(nome="Algoritmo")

        quiz = Quiz.objects.create(
            disciplina=disciplina,
            titulo="Quiz de Algoritmo",
            tipo_prova="ENADE",
        )

        Tentativa.objects.create(
            usuario=self.estudante,
            quiz=quiz,
            tipo_tentativa="QUIZ",
            quantidade_acertos=4,
            quantidade_erros=1,
            percentual_acertos=80,
            pontuacao=20,
            concluida=True,
        )

        Tentativa.objects.create(
            usuario=self.admin,
            quiz=quiz,
            tipo_tentativa="QUIZ",
            quantidade_acertos=2,
            quantidade_erros=2,
            percentual_acertos=50,
            pontuacao=10,
            concluida=True,
        )

        self.client.login(username="estudante", password="123456")

        response = self.client.get(reverse("ranking_estudante"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("ranking", response.context)
        self.assertIn("top_3", response.context)
        self.assertIn("ranking_restante", response.context)
        self.assertIn("minha_posicao", response.context)
        self.assertEqual(response.context["minha_posicao"]["usuario__id"], self.estudante.id)

    def test_admin_nao_acessa_ranking_estudante(self):
        self.client.login(username="admin", password="123456")

        response = self.client.get(reverse("ranking_estudante"))

        self.assertEqual(response.status_code, 302)

    # def test_admin_acessa_desempenho_geral(self):
    #     disciplina = Disciplina.objects.create(nome="Algoritmo")

    #     quiz = Quiz.objects.create(
    #         disciplina=disciplina,
    #         titulo="Quiz de Algoritmo",
    #         tipo_prova="ENADE",
    #     )

    #     Tentativa.objects.create(
    #         usuario=self.estudante,
    #         quiz=quiz,
    #         tipo_tentativa="QUIZ",
    #         quantidade_acertos=3,
    #         quantidade_erros=1,
    #         percentual_acertos=75,
    #         pontuacao=15,
    #         concluida=True,
    #     )

    #     self.client.login(username="admin", password="123456")

    #     response = self.client.get(reverse("admin_desempenho_geral"))

    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn("total_tentativas", response.context)
    #     self.assertIn("total_estudantes_ativos", response.context)
    #     self.assertIn("taxa_media_acerto", response.context)
    #     self.assertIn("pontuacao_total", response.context)
    #     self.assertIn("ranking_estudantes", response.context)
    #     self.assertIn("quizzes_populares", response.context)

    #     self.assertEqual(response.context["total_tentativas"], 1)
    #     self.assertEqual(response.context["total_estudantes_ativos"], 1)
    #     self.assertEqual(response.context["taxa_media_acerto"], 75)
    #     self.assertEqual(response.context["pontuacao_total"], 15)

    # def test_estudante_nao_acessa_desempenho_geral_admin(self):
    #     self.client.login(username="estudante", password="123456")

    #     response = self.client.get(reverse("admin_desempenho_geral"))

    #     self.assertEqual(response.status_code, 302)
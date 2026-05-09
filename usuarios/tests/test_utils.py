from django.test import TestCase

from disciplinas.models import Disciplina
from quizzes.models import Quiz, Tentativa
from usuarios.models import Usuario, TipoUsuario
from usuarios.utils import (
    usuario_e_admin,
    usuario_e_estudante,
    calcular_progresso_nivel,
    calcular_taxa_acerto,
    calcular_resumo_tentativas_quiz,
    montar_desempenho_por_area,
    adicionar_posicoes_ranking,
)


class UsuariosUtilsTest(TestCase):
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

        self.disciplina = Disciplina.objects.create(nome="Algoritmo")

        self.quiz = Quiz.objects.create(
            disciplina=self.disciplina,
            titulo="Quiz de Algoritmo",
            tipo_prova="ENADE",
        )

    def test_usuario_e_admin(self):
        self.assertTrue(usuario_e_admin(self.admin))
        self.assertFalse(usuario_e_admin(self.estudante))

    def test_usuario_e_estudante(self):
        self.assertTrue(usuario_e_estudante(self.estudante))
        self.assertFalse(usuario_e_estudante(self.admin))

    def test_calcular_progresso_nivel_inicial(self):
        progresso = calcular_progresso_nivel(0)

        self.assertEqual(progresso["nivel_atual"], 1)
        self.assertEqual(progresso["xp_total"], 0)
        self.assertEqual(progresso["xp_no_nivel"], 0)
        self.assertEqual(progresso["xp_para_proximo_nivel"], 100)
        self.assertEqual(progresso["xp_faltante"], 100)
        self.assertEqual(progresso["percentual_nivel"], 0)

    def test_calcular_progresso_nivel_com_50_xp(self):
        progresso = calcular_progresso_nivel(50)

        self.assertEqual(progresso["nivel_atual"], 1)
        self.assertEqual(progresso["xp_total"], 50)
        self.assertEqual(progresso["xp_no_nivel"], 50)
        self.assertEqual(progresso["xp_para_proximo_nivel"], 100)
        self.assertEqual(progresso["xp_faltante"], 50)
        self.assertEqual(progresso["percentual_nivel"], 50)

    def test_calcular_progresso_nivel_ao_passar_de_nivel(self):
        progresso = calcular_progresso_nivel(100)

        self.assertEqual(progresso["nivel_atual"], 2)
        self.assertEqual(progresso["xp_total"], 100)
        self.assertEqual(progresso["xp_inicio_nivel"], 100)
        self.assertEqual(progresso["xp_no_nivel"], 0)
        self.assertEqual(progresso["xp_para_proximo_nivel"], 200)
        self.assertEqual(progresso["xp_faltante"], 200)
        self.assertEqual(progresso["percentual_nivel"], 0)

    def test_calcular_taxa_acerto(self):
        self.assertEqual(calcular_taxa_acerto(0, 0), 0)
        self.assertEqual(calcular_taxa_acerto(5, 10), 50)
        self.assertEqual(calcular_taxa_acerto(7, 10), 70)
        self.assertEqual(calcular_taxa_acerto(3, 4), 75)

    def test_calcular_resumo_tentativas_quiz_sem_tentativas(self):
        tentativas = Tentativa.objects.filter(
            usuario=self.estudante,
            tipo_tentativa="QUIZ",
            concluida=True,
        )

        resumo = calcular_resumo_tentativas_quiz(tentativas)

        self.assertEqual(resumo["total_quizzes"], 0)
        self.assertEqual(resumo["total_acertos"], 0)
        self.assertEqual(resumo["total_erros"], 0)
        self.assertEqual(resumo["total_questoes"], 0)
        self.assertEqual(resumo["xp_total"], 0)
        self.assertEqual(resumo["taxa_acerto"], 0)
        self.assertEqual(resumo["progresso_nivel"]["nivel_atual"], 1)

    def test_calcular_resumo_tentativas_quiz_com_tentativas(self):
        Tentativa.objects.create(
            usuario=self.estudante,
            quiz=self.quiz,
            tipo_tentativa="QUIZ",
            quantidade_acertos=3,
            quantidade_erros=1,
            percentual_acertos=75,
            pontuacao=15,
            concluida=True,
        )

        Tentativa.objects.create(
            usuario=self.estudante,
            quiz=self.quiz,
            tipo_tentativa="QUIZ",
            quantidade_acertos=1,
            quantidade_erros=1,
            percentual_acertos=50,
            pontuacao=5,
            concluida=True,
        )

        tentativas = Tentativa.objects.filter(
            usuario=self.estudante,
            tipo_tentativa="QUIZ",
            concluida=True,
        )

        resumo = calcular_resumo_tentativas_quiz(tentativas)

        self.assertEqual(resumo["total_quizzes"], 2)
        self.assertEqual(resumo["total_acertos"], 4)
        self.assertEqual(resumo["total_erros"], 2)
        self.assertEqual(resumo["total_questoes"], 6)
        self.assertEqual(resumo["xp_total"], 20)
        self.assertEqual(resumo["taxa_acerto"], 66.7)

    def test_montar_desempenho_por_area(self):
        desempenho_por_area_qs = [
            {
                "quiz__disciplina__nome": "Algoritmo",
                "media_acerto": 80.0,
            },
            {
                "quiz__disciplina__nome": "Banco de Dados",
                "media_acerto": 60.0,
            },
        ]

        desempenho = montar_desempenho_por_area(desempenho_por_area_qs)

        self.assertEqual(desempenho["labels_area"], ["Algoritmo", "Banco de Dados"])
        self.assertEqual(desempenho["dados_area"], [80.0, 60.0])
        self.assertEqual(desempenho["melhor_area"]["disciplina"], "Algoritmo")
        self.assertEqual(desempenho["pior_area"]["disciplina"], "Banco de Dados")

    def test_montar_desempenho_por_area_vazio(self):
        desempenho = montar_desempenho_por_area([])

        self.assertEqual(desempenho["labels_area"], [])
        self.assertEqual(desempenho["dados_area"], [])
        self.assertEqual(desempenho["desempenho_detalhado"], [])
        self.assertIsNone(desempenho["melhor_area"])
        self.assertIsNone(desempenho["pior_area"])

    def test_adicionar_posicoes_ranking(self):
        ranking = [
            {
                "usuario__id": self.admin.id,
                "usuario__nome": self.admin.nome,
                "usuario__username": self.admin.username,
                "total_pontos": 30,
                "total_acertos": 6,
                "total_erros": 2,
                "total_tentativas": 2,
            },
            {
                "usuario__id": self.estudante.id,
                "usuario__nome": self.estudante.nome,
                "usuario__username": self.estudante.username,
                "total_pontos": 20,
                "total_acertos": 4,
                "total_erros": 1,
                "total_tentativas": 1,
            },
        ]

        dados = adicionar_posicoes_ranking(
            ranking=ranking,
            usuario_id=self.estudante.id,
        )

        self.assertEqual(len(dados["ranking"]), 2)
        self.assertEqual(dados["ranking"][0]["posicao"], 1)
        self.assertEqual(dados["ranking"][1]["posicao"], 2)
        self.assertEqual(dados["ranking"][1]["taxa_acerto"], 80)
        self.assertEqual(dados["minha_posicao"]["usuario__id"], self.estudante.id)
        self.assertEqual(dados["minha_posicao"]["posicao"], 2)
        self.assertEqual(len(dados["top_3"]), 2)
        self.assertEqual(len(dados["ranking_restante"]), 0)
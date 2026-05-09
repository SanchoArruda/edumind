from datetime import timedelta

from django.test import TestCase

from disciplinas.models import Disciplina
from quizzes.models import Questao, Alternativa, Quiz, Tentativa
from usuarios.models import Usuario, TipoUsuario


class QuestaoModelTest(TestCase):
    def setUp(self):
        self.disciplina = Disciplina.objects.create(nome="Algoritmo")

    def test_criar_questao(self):
        questao = Questao.objects.create(
            disciplina=self.disciplina,
            enunciado="Quanto é 2 + 2?",
            explicacao_resposta="A soma de 2 + 2 é 4.",
            nivel_dificuldade="FACIL",
            tipo_prova="ENADE",
        )

        self.assertEqual(questao.disciplina, self.disciplina)
        self.assertEqual(questao.enunciado, "Quanto é 2 + 2?")
        self.assertEqual(questao.nivel_dificuldade, "FACIL")
        self.assertEqual(questao.tipo_prova, "ENADE")
        self.assertIn("Questão", str(questao))
        self.assertIn("Algoritmo", str(questao))


class AlternativaModelTest(TestCase):
    def setUp(self):
        self.disciplina = Disciplina.objects.create(nome="Algoritmo")
        self.questao = Questao.objects.create(
            disciplina=self.disciplina,
            enunciado="Quanto é 2 + 2?",
            nivel_dificuldade="FACIL",
            tipo_prova="ENADE",
        )

    def test_criar_alternativa(self):
        alternativa = Alternativa.objects.create(
            questao=self.questao,
            letra="A",
            texto="4",
            correta=True,
        )

        self.assertEqual(alternativa.questao, self.questao)
        self.assertEqual(alternativa.letra, "A")
        self.assertEqual(alternativa.texto, "4")
        self.assertTrue(alternativa.correta)
        self.assertEqual(str(alternativa), "A) 4")

    def test_questao_pode_ter_varias_alternativas(self):
        Alternativa.objects.create(
            questao=self.questao,
            letra="A",
            texto="3",
            correta=False,
        )
        Alternativa.objects.create(
            questao=self.questao,
            letra="B",
            texto="4",
            correta=True,
        )

        self.assertEqual(self.questao.alternativas.count(), 2)
        self.assertTrue(self.questao.alternativas.filter(correta=True).exists())


class QuizModelTest(TestCase):
    def setUp(self):
        self.disciplina = Disciplina.objects.create(nome="Banco de Dados")

    def test_criar_quiz(self):
        quiz = Quiz.objects.create(
            disciplina=self.disciplina,
            titulo="Quiz de Banco de Dados",
            descricao="Quiz sobre conceitos básicos.",
            tipo_prova="ENADE",
        )

        self.assertEqual(quiz.titulo, "Quiz de Banco de Dados")
        self.assertEqual(quiz.disciplina, self.disciplina)
        self.assertEqual(quiz.tipo_prova, "ENADE")
        self.assertEqual(str(quiz), "Quiz de Banco de Dados")

    def test_quiz_pode_ter_questoes(self):
        quiz = Quiz.objects.create(
            disciplina=self.disciplina,
            titulo="Quiz de Banco de Dados",
            tipo_prova="ENADE",
        )

        questao = Questao.objects.create(
            disciplina=self.disciplina,
            enunciado="O que é uma chave primária?",
            nivel_dificuldade="MEDIA",
            tipo_prova="ENADE",
        )

        quiz.questoes.add(questao)

        self.assertEqual(quiz.questoes.count(), 1)
        self.assertEqual(questao.quizzes.count(), 1)


class TentativaModelTest(TestCase):
    def setUp(self):
        tipo_estudante = TipoUsuario.objects.create(perfil="Estudante")

        self.usuario = Usuario.objects.create_user(
            username="estudante",
            nome="Estudante Teste",
            email="estudante@email.com",
            password="123456",
            tipo_usuario=tipo_estudante,
        )

        self.disciplina = Disciplina.objects.create(nome="Algoritmo")

        self.quiz = Quiz.objects.create(
            disciplina=self.disciplina,
            titulo="Quiz Teste",
            tipo_prova="ENADE",
        )

    def test_criar_tentativa_quiz(self):
        tentativa = Tentativa.objects.create(
            usuario=self.usuario,
            quiz=self.quiz,
            tipo_tentativa="QUIZ",
            pontuacao=10,
            quantidade_acertos=2,
            quantidade_erros=1,
            percentual_acertos=66.67,
            desempenho_geral="Bom esforço!",
            concluida=True,
        )

        self.assertEqual(tentativa.usuario, self.usuario)
        self.assertEqual(tentativa.quiz, self.quiz)
        self.assertEqual(tentativa.tipo_tentativa, "QUIZ")
        self.assertTrue(tentativa.concluida)
        self.assertEqual(tentativa.pontuacao, 10)
        self.assertIn("Quiz", str(tentativa))

    def test_tempo_formatado_segundos(self):
        tentativa = Tentativa.objects.create(
            usuario=self.usuario,
            quiz=self.quiz,
            tipo_tentativa="QUIZ",
            tempo_gasto=timedelta(seconds=7),
            concluida=True,
        )

        self.assertEqual(tentativa.tempo_formatado, "7 seg")

    def test_tempo_formatado_minutos_e_segundos(self):
        tentativa = Tentativa.objects.create(
            usuario=self.usuario,
            quiz=self.quiz,
            tipo_tentativa="QUIZ",
            tempo_gasto=timedelta(seconds=69),
            concluida=True,
        )

        self.assertEqual(tentativa.tempo_formatado, "1 min e 9 seg")

    def test_tempo_formatado_nao_registrado(self):
        tentativa = Tentativa.objects.create(
            usuario=self.usuario,
            quiz=self.quiz,
            tipo_tentativa="QUIZ",
            concluida=True,
        )

        self.assertEqual(tentativa.tempo_formatado, "Não registrado")
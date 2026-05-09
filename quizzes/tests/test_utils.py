from datetime import timedelta

from django.test import TestCase
from django.utils.datastructures import MultiValueDict

from disciplinas.models import Disciplina
from quizzes.models import Alternativa, Questao, Quiz, Tentativa
from quizzes.utils import (
    calcular_percentual_acertos,
    calcular_xp_tentativa,
    corrigir_respostas_quiz,
    finalizar_tentativa_quiz,
    montar_revisao_quiz,
    obter_emoji_resultado_quiz,
    obter_mensagem_resultado_quiz,
)
from usuarios.models import TipoUsuario, Usuario


class QuizUtilsTest(TestCase):
    def setUp(self):
        self.tipo_estudante = TipoUsuario.objects.create(perfil="Estudante")

        self.usuario = Usuario.objects.create_user(
            username="estudante_utils",
            nome="Estudante Utils",
            email="utils@email.com",
            password="123456",
            tipo_usuario=self.tipo_estudante,
        )

        self.disciplina = Disciplina.objects.create(nome="Algoritmos")

        self.quiz = Quiz.objects.create(
            disciplina=self.disciplina,
            titulo="Quiz de Teste",
            descricao="Descrição do quiz",
            tipo_prova="ENADE",
        )

        self.questao = Questao.objects.create(
            disciplina=self.disciplina,
            enunciado="Quanto é 2 + 2?",
            explicacao_resposta="A resposta correta é 4.",
            nivel_dificuldade="FACIL",
            tipo_prova="ENADE",
        )

        self.alternativa_errada = Alternativa.objects.create(
            questao=self.questao,
            letra="A",
            texto="3",
            correta=False,
        )

        self.alternativa_correta = Alternativa.objects.create(
            questao=self.questao,
            letra="B",
            texto="4",
            correta=True,
        )

        self.quiz.questoes.add(self.questao)

    def criar_tentativa(self):
        return Tentativa.objects.create(
            usuario=self.usuario,
            quiz=self.quiz,
            tipo_tentativa="QUIZ",
            pontuacao=0,
            quantidade_acertos=0,
            quantidade_erros=0,
            percentual_acertos=0,
            desempenho_geral="",
            concluida=False,
            aprovado=False,
        )

    def test_calcular_xp_tentativa(self):
        self.assertEqual(calcular_xp_tentativa(0), 0)
        self.assertEqual(calcular_xp_tentativa(1), 5)
        self.assertEqual(calcular_xp_tentativa(4), 20)

    def test_calcular_percentual_acertos(self):
        self.assertEqual(calcular_percentual_acertos(0, 0), 0)
        self.assertEqual(calcular_percentual_acertos(0, 5), 0)
        self.assertEqual(calcular_percentual_acertos(1, 2), 50)
        self.assertEqual(calcular_percentual_acertos(2, 3), 66.67)
        self.assertEqual(calcular_percentual_acertos(3, 3), 100)

    def test_obter_mensagem_resultado_quiz(self):
        self.assertEqual(
            obter_mensagem_resultado_quiz(100),
            "Excelente desempenho!"
        )
        self.assertEqual(
            obter_mensagem_resultado_quiz(70),
            "Muito bem! Continue assim!"
        )
        self.assertEqual(
            obter_mensagem_resultado_quiz(40),
            "Bom esforço! Continue praticando!"
        )
        self.assertEqual(
            obter_mensagem_resultado_quiz(39),
            "Continue praticando!"
        )

    def test_obter_emoji_resultado_quiz(self):
        self.assertEqual(obter_emoji_resultado_quiz(100), "🏆")
        self.assertEqual(obter_emoji_resultado_quiz(70), "🎉")
        self.assertEqual(obter_emoji_resultado_quiz(40), "👏")
        self.assertEqual(obter_emoji_resultado_quiz(39), "💪")

    def test_corrigir_respostas_quiz_com_resposta_correta(self):
        post_data = {
            f"questao_{self.questao.id}": str(self.alternativa_correta.id)
        }

        resultado = corrigir_respostas_quiz(
            questoes=self.quiz.questoes.all(),
            post_data=post_data,
        )

        self.assertEqual(resultado["quantidade_acertos"], 1)
        self.assertEqual(resultado["quantidade_erros"], 0)
        self.assertEqual(
            resultado["respostas_usuario"][str(self.questao.id)],
            self.alternativa_correta.id,
        )

    def test_corrigir_respostas_quiz_com_resposta_errada(self):
        post_data = {
            f"questao_{self.questao.id}": str(self.alternativa_errada.id)
        }

        resultado = corrigir_respostas_quiz(
            questoes=self.quiz.questoes.all(),
            post_data=post_data,
        )

        self.assertEqual(resultado["quantidade_acertos"], 0)
        self.assertEqual(resultado["quantidade_erros"], 1)
        self.assertEqual(
            resultado["respostas_usuario"][str(self.questao.id)],
            self.alternativa_errada.id,
        )

    def test_corrigir_respostas_quiz_sem_resposta_marca_como_erro(self):
        resultado = corrigir_respostas_quiz(
            questoes=self.quiz.questoes.all(),
            post_data={},
        )

        self.assertEqual(resultado["quantidade_acertos"], 0)
        self.assertEqual(resultado["quantidade_erros"], 1)
        self.assertEqual(resultado["respostas_usuario"], {})

    def test_corrigir_respostas_quiz_com_alternativa_de_outra_questao_marca_como_erro(self):
        outra_questao = Questao.objects.create(
            disciplina=self.disciplina,
            enunciado="Quanto é 5 + 5?",
            explicacao_resposta="A resposta correta é 10.",
            nivel_dificuldade="FACIL",
            tipo_prova="ENADE",
        )

        alternativa_outra_questao = Alternativa.objects.create(
            questao=outra_questao,
            letra="A",
            texto="10",
            correta=True,
        )

        post_data = {
            f"questao_{self.questao.id}": str(alternativa_outra_questao.id)
        }

        resultado = corrigir_respostas_quiz(
            questoes=self.quiz.questoes.all(),
            post_data=post_data,
        )

        self.assertEqual(resultado["quantidade_acertos"], 0)
        self.assertEqual(resultado["quantidade_erros"], 1)

    def test_finalizar_tentativa_quiz_com_tempo_informado(self):
        tentativa = self.criar_tentativa()

        post_data = {
            f"questao_{self.questao.id}": str(self.alternativa_correta.id),
            "tempo_gasto_segundos": "75",
        }

        tentativa = finalizar_tentativa_quiz(
            tentativa=tentativa,
            questoes=self.quiz.questoes.all(),
            post_data=post_data,
        )

        tentativa.refresh_from_db()

        self.assertTrue(tentativa.concluida)
        self.assertEqual(tentativa.quantidade_acertos, 1)
        self.assertEqual(tentativa.quantidade_erros, 0)
        self.assertEqual(tentativa.percentual_acertos, 100)
        self.assertEqual(tentativa.pontuacao, 5)
        self.assertEqual(tentativa.desempenho_geral, "Excelente desempenho!")
        self.assertEqual(tentativa.tempo_gasto, timedelta(seconds=75))
        self.assertFalse(tentativa.aprovado)
        self.assertEqual(
            tentativa.respostas[str(self.questao.id)],
            self.alternativa_correta.id,
        )

    def test_finalizar_tentativa_quiz_sem_tempo_usa_zero_segundos(self):
        tentativa = self.criar_tentativa()

        post_data = {
            f"questao_{self.questao.id}": str(self.alternativa_errada.id),
        }

        finalizar_tentativa_quiz(
            tentativa=tentativa,
            questoes=self.quiz.questoes.all(),
            post_data=post_data,
        )

        tentativa.refresh_from_db()

        self.assertEqual(tentativa.tempo_gasto, timedelta(seconds=0))
        self.assertEqual(tentativa.quantidade_acertos, 0)
        self.assertEqual(tentativa.quantidade_erros, 1)
        self.assertEqual(tentativa.percentual_acertos, 0)
        self.assertEqual(tentativa.pontuacao, 0)
        self.assertEqual(tentativa.desempenho_geral, "Continue praticando!")

    def test_montar_revisao_quiz_com_resposta_correta(self):
        respostas_usuario = {
            str(self.questao.id): self.alternativa_correta.id
        }

        revisao = montar_revisao_quiz(
            questoes=self.quiz.questoes.all(),
            respostas_usuario=respostas_usuario,
        )

        self.assertEqual(len(revisao), 1)
        self.assertEqual(revisao[0]["numero"], 1)
        self.assertEqual(revisao[0]["questao"], self.questao)
        self.assertEqual(len(revisao[0]["alternativas"]), 2)
        self.assertEqual(
            revisao[0]["alternativa_correta_id"],
            str(self.alternativa_correta.id),
        )
        self.assertEqual(
            revisao[0]["alternativa_marcada_id"],
            str(self.alternativa_correta.id),
        )
        self.assertTrue(revisao[0]["acertou"])
        self.assertEqual(revisao[0]["explicacao"], "A resposta correta é 4.")

    def test_montar_revisao_quiz_com_resposta_errada(self):
        respostas_usuario = {
            str(self.questao.id): self.alternativa_errada.id
        }

        revisao = montar_revisao_quiz(
            questoes=self.quiz.questoes.all(),
            respostas_usuario=respostas_usuario,
        )

        self.assertFalse(revisao[0]["acertou"])
        self.assertEqual(
            revisao[0]["alternativa_marcada_id"],
            str(self.alternativa_errada.id),
        )

    def test_montar_revisao_quiz_sem_resposta_marcada(self):
        revisao = montar_revisao_quiz(
            questoes=self.quiz.questoes.all(),
            respostas_usuario={},
        )

        self.assertFalse(revisao[0]["acertou"])
        self.assertIsNone(revisao[0]["alternativa_marcada_id"])

    def test_montar_revisao_quiz_sem_alternativa_correta(self):
        questao_sem_correta = Questao.objects.create(
            disciplina=self.disciplina,
            enunciado="Questão sem correta",
            explicacao_resposta="Sem explicação.",
            nivel_dificuldade="FACIL",
            tipo_prova="ENADE",
        )

        Alternativa.objects.create(
            questao=questao_sem_correta,
            letra="A",
            texto="Alternativa A",
            correta=False,
        )

        revisao = montar_revisao_quiz(
            questoes=Questao.objects.filter(id=questao_sem_correta.id),
            respostas_usuario={},
        )

        self.assertFalse(revisao[0]["acertou"])
        self.assertIsNone(revisao[0]["alternativa_correta_id"])
        self.assertIsNone(revisao[0]["alternativa_marcada_id"])
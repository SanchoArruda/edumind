from datetime import timedelta

from django.test import TestCase

from desafios.models import Desafio
from desafios.utils import (
    calcular_estrelas_desafio,
    calcular_percentual_desafio,
    corrigir_respostas_desafio,
    finalizar_tentativa_desafio,
    montar_revisao_desafio,
    obter_emoji_desafio,
    obter_mensagem_desafio,
)
from disciplinas.models import Disciplina
from quizzes.models import Alternativa, Questao, Tentativa
from usuarios.models import TipoUsuario, Usuario


class DesafioUtilsTest(TestCase):
    def setUp(self):
        self.tipo_estudante = TipoUsuario.objects.create(perfil="Estudante")

        self.usuario = Usuario.objects.create_user(
            username="estudante_utils",
            nome="Estudante Utils",
            email="estudante_utils@email.com",
            password="123456",
            tipo_usuario=self.tipo_estudante,
        )

        self.disciplina = Disciplina.objects.create(nome="Algoritmo")

        self.questao_1 = Questao.objects.create(
            disciplina=self.disciplina,
            enunciado="Quanto é 2 + 2?",
            explicacao_resposta="A resposta correta é 4.",
            nivel_dificuldade="FACIL",
            tipo_prova="ENADE",
        )

        self.alternativa_1_errada = Alternativa.objects.create(
            questao=self.questao_1,
            letra="A",
            texto="3",
            correta=False,
        )

        self.alternativa_1_correta = Alternativa.objects.create(
            questao=self.questao_1,
            letra="B",
            texto="4",
            correta=True,
        )

        self.questao_2 = Questao.objects.create(
            disciplina=self.disciplina,
            enunciado="Quanto é 3 + 3?",
            explicacao_resposta="A resposta correta é 6.",
            nivel_dificuldade="FACIL",
            tipo_prova="ENADE",
        )

        self.alternativa_2_errada = Alternativa.objects.create(
            questao=self.questao_2,
            letra="A",
            texto="5",
            correta=False,
        )

        self.alternativa_2_correta = Alternativa.objects.create(
            questao=self.questao_2,
            letra="B",
            texto="6",
            correta=True,
        )

        self.desafio = Desafio.objects.create(
            titulo="Desafio 1 — Algoritmo",
            tipo_prova="ENADE",
            nivel=1,
            ordem=1,
            quantidade_questoes=2,
            tempo_total_segundos=600,
            ativo=True,
        )

        self.desafio.questoes.set([
            self.questao_1,
            self.questao_2,
        ])

    def criar_tentativa(self):
        return Tentativa.objects.create(
            usuario=self.usuario,
            desafio=self.desafio,
            tipo_tentativa="DESAFIO",
            pontuacao=0,
            quantidade_acertos=0,
            quantidade_erros=0,
            percentual_acertos=0,
            desempenho_geral="",
            concluida=False,
            aprovado=False,
        )

    def test_calcular_estrelas_desafio(self):
        self.assertEqual(calcular_estrelas_desafio(0), 0)
        self.assertEqual(calcular_estrelas_desafio(10), 1)
        self.assertEqual(calcular_estrelas_desafio(20), 2)
        self.assertEqual(calcular_estrelas_desafio(40), 3)
        self.assertEqual(calcular_estrelas_desafio(60), 4)
        self.assertEqual(calcular_estrelas_desafio(80), 5)
        self.assertEqual(calcular_estrelas_desafio(100), 5)

    def test_obter_mensagem_desafio(self):
        self.assertEqual(
            obter_mensagem_desafio(5),
            "Excelente desempenho!"
        )
        self.assertEqual(
            obter_mensagem_desafio(4),
            "Muito bem!"
        )
        self.assertEqual(
            obter_mensagem_desafio(3),
            "Bom esforço!"
        )
        self.assertEqual(
            obter_mensagem_desafio(2),
            "Você está evoluindo!"
        )
        self.assertEqual(
            obter_mensagem_desafio(1),
            "Continue treinando!"
        )
        self.assertEqual(
            obter_mensagem_desafio(0),
            "Continue treinando!"
        )

    def test_obter_emoji_desafio(self):
        self.assertEqual(obter_emoji_desafio(5), "🏆")
        self.assertEqual(obter_emoji_desafio(4), "🎉")
        self.assertEqual(obter_emoji_desafio(3), "💪")
        self.assertEqual(obter_emoji_desafio(2), "📚")
        self.assertEqual(obter_emoji_desafio(0), "📚")

    def test_calcular_percentual_desafio(self):
        self.assertEqual(calcular_percentual_desafio(0, 0), 0)
        self.assertEqual(calcular_percentual_desafio(0, 2), 0)
        self.assertEqual(calcular_percentual_desafio(1, 2), 50)
        self.assertEqual(calcular_percentual_desafio(2, 3), 66.67)
        self.assertEqual(calcular_percentual_desafio(2, 2), 100)

    def test_corrigir_respostas_desafio_com_todas_corretas(self):
        post_data = {
            f"questao_{self.questao_1.id}": str(self.alternativa_1_correta.id),
            f"questao_{self.questao_2.id}": str(self.alternativa_2_correta.id),
        }

        resultado = corrigir_respostas_desafio(
            questoes=self.desafio.questoes.all(),
            post_data=post_data,
        )

        self.assertEqual(resultado["quantidade_acertos"], 2)
        self.assertEqual(resultado["quantidade_erros"], 0)
        self.assertEqual(
            resultado["respostas_usuario"][str(self.questao_1.id)],
            self.alternativa_1_correta.id,
        )

    def test_corrigir_respostas_desafio_com_uma_errada(self):
        post_data = {
            f"questao_{self.questao_1.id}": str(self.alternativa_1_correta.id),
            f"questao_{self.questao_2.id}": str(self.alternativa_2_errada.id),
        }

        resultado = corrigir_respostas_desafio(
            questoes=self.desafio.questoes.all(),
            post_data=post_data,
        )

        self.assertEqual(resultado["quantidade_acertos"], 1)
        self.assertEqual(resultado["quantidade_erros"], 1)

    def test_corrigir_respostas_desafio_sem_responder_marca_erro(self):
        post_data = {
            f"questao_{self.questao_1.id}": str(self.alternativa_1_correta.id),
        }

        resultado = corrigir_respostas_desafio(
            questoes=self.desafio.questoes.all(),
            post_data=post_data,
        )

        self.assertEqual(resultado["quantidade_acertos"], 1)
        self.assertEqual(resultado["quantidade_erros"], 1)

    def test_corrigir_respostas_desafio_com_alternativa_de_outra_questao_marca_erro(self):
        post_data = {
            f"questao_{self.questao_1.id}": str(self.alternativa_2_correta.id),
            f"questao_{self.questao_2.id}": str(self.alternativa_2_correta.id),
        }

        resultado = corrigir_respostas_desafio(
            questoes=self.desafio.questoes.all(),
            post_data=post_data,
        )

        self.assertEqual(resultado["quantidade_acertos"], 1)
        self.assertEqual(resultado["quantidade_erros"], 1)

    def test_finalizar_tentativa_desafio_aprovado(self):
        tentativa = self.criar_tentativa()

        post_data = {
            f"questao_{self.questao_1.id}": str(self.alternativa_1_correta.id),
            f"questao_{self.questao_2.id}": str(self.alternativa_2_correta.id),
            "tempo_gasto_segundos": "75",
        }

        finalizar_tentativa_desafio(
            tentativa=tentativa,
            questoes=self.desafio.questoes.all(),
            post_data=post_data,
        )

        tentativa.refresh_from_db()

        self.assertTrue(tentativa.concluida)
        self.assertTrue(tentativa.aprovado)
        self.assertEqual(tentativa.quantidade_acertos, 2)
        self.assertEqual(tentativa.quantidade_erros, 0)
        self.assertEqual(tentativa.percentual_acertos, 100)
        self.assertEqual(tentativa.pontuacao, 5)
        self.assertEqual(tentativa.desempenho_geral, "Excelente desempenho!")
        self.assertEqual(tentativa.tempo_gasto, timedelta(seconds=75))

    def test_finalizar_tentativa_desafio_reprovado(self):
        tentativa = self.criar_tentativa()

        post_data = {
            f"questao_{self.questao_1.id}": str(self.alternativa_1_correta.id),
            f"questao_{self.questao_2.id}": str(self.alternativa_2_errada.id),
            "tempo_gasto_segundos": "30",
        }

        finalizar_tentativa_desafio(
            tentativa=tentativa,
            questoes=self.desafio.questoes.all(),
            post_data=post_data,
        )

        tentativa.refresh_from_db()

        self.assertTrue(tentativa.concluida)
        self.assertFalse(tentativa.aprovado)
        self.assertEqual(tentativa.quantidade_acertos, 1)
        self.assertEqual(tentativa.quantidade_erros, 1)
        self.assertEqual(tentativa.percentual_acertos, 50)
        self.assertEqual(tentativa.pontuacao, 3)
        self.assertEqual(tentativa.desempenho_geral, "Bom esforço!")
        self.assertEqual(tentativa.tempo_gasto, timedelta(seconds=30))

    def test_finalizar_tentativa_desafio_sem_tempo_usa_zero(self):
        tentativa = self.criar_tentativa()

        post_data = {
            f"questao_{self.questao_1.id}": str(self.alternativa_1_errada.id),
            f"questao_{self.questao_2.id}": str(self.alternativa_2_errada.id),
        }

        finalizar_tentativa_desafio(
            tentativa=tentativa,
            questoes=self.desafio.questoes.all(),
            post_data=post_data,
        )

        tentativa.refresh_from_db()

        self.assertEqual(tentativa.tempo_gasto, timedelta(seconds=0))
        self.assertEqual(tentativa.percentual_acertos, 0)
        self.assertEqual(tentativa.pontuacao, 0)
        self.assertFalse(tentativa.aprovado)

    def test_montar_revisao_desafio_com_respostas(self):
        respostas_usuario = {
            str(self.questao_1.id): self.alternativa_1_correta.id,
            str(self.questao_2.id): self.alternativa_2_errada.id,
        }

        revisao = montar_revisao_desafio(
            questoes=self.desafio.questoes.all(),
            respostas_usuario=respostas_usuario,
        )

        self.assertEqual(len(revisao), 2)

        self.assertEqual(revisao[0]["numero"], 1)
        self.assertEqual(revisao[0]["questao"], self.questao_1)
        self.assertTrue(revisao[0]["acertou"])
        self.assertEqual(
            revisao[0]["alternativa_correta_id"],
            str(self.alternativa_1_correta.id),
        )
        self.assertEqual(
            revisao[0]["alternativa_marcada_id"],
            str(self.alternativa_1_correta.id),
        )

        self.assertEqual(revisao[1]["numero"], 2)
        self.assertEqual(revisao[1]["questao"], self.questao_2)
        self.assertFalse(revisao[1]["acertou"])
        self.assertEqual(
            revisao[1]["alternativa_correta_id"],
            str(self.alternativa_2_correta.id),
        )
        self.assertEqual(
            revisao[1]["alternativa_marcada_id"],
            str(self.alternativa_2_errada.id),
        )

    def test_montar_revisao_desafio_sem_resposta_marcada(self):
        revisao = montar_revisao_desafio(
            questoes=self.desafio.questoes.all(),
            respostas_usuario={},
        )

        self.assertEqual(len(revisao), 2)
        self.assertFalse(revisao[0]["acertou"])
        self.assertIsNone(revisao[0]["alternativa_marcada_id"])

    def test_montar_revisao_desafio_sem_alternativa_correta(self):
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

        revisao = montar_revisao_desafio(
            questoes=Questao.objects.filter(id=questao_sem_correta.id),
            respostas_usuario={},
        )

        self.assertEqual(len(revisao), 1)
        self.assertFalse(revisao[0]["acertou"])
        self.assertIsNone(revisao[0]["alternativa_correta_id"])
        self.assertIsNone(revisao[0]["alternativa_marcada_id"])
from django.db import IntegrityError
from django.test import TestCase

from desafios.models import Desafio
from disciplinas.models import Disciplina
from quizzes.models import Questao


class DesafioModelTest(TestCase):
    def setUp(self):
        self.disciplina = Disciplina.objects.create(nome="Algoritmo")

        self.questao = Questao.objects.create(
            disciplina=self.disciplina,
            enunciado="Quanto é 2 + 2?",
            nivel_dificuldade="FACIL",
            tipo_prova="ENADE",
        )

    def test_criar_desafio_enade(self):
        desafio = Desafio.objects.create(
            titulo="Desafio 1 — Algoritmo",
            tipo_prova="ENADE",
            nivel=1,
            ordem=1,
            quantidade_questoes=5,
            tempo_total_segundos=600,
            ativo=True,
        )

        self.assertEqual(desafio.titulo, "Desafio 1 — Algoritmo")
        self.assertEqual(desafio.tipo_prova, "ENADE")
        self.assertEqual(desafio.nivel, 1)
        self.assertEqual(desafio.ordem, 1)
        self.assertEqual(desafio.quantidade_questoes, 5)
        self.assertEqual(desafio.tempo_total_segundos, 600)
        self.assertTrue(desafio.ativo)
        self.assertEqual(str(desafio), "Desafio 1 — Algoritmo (ENADE)")

    def test_desafio_pode_ter_questoes(self):
        desafio = Desafio.objects.create(
            titulo="Desafio 1 — Algoritmo",
            tipo_prova="ENADE",
            nivel=1,
            ordem=1,
            quantidade_questoes=1,
            tempo_total_segundos=300,
            ativo=True,
        )

        desafio.questoes.add(self.questao)

        self.assertEqual(desafio.questoes.count(), 1)
        self.assertEqual(self.questao.desafios.count(), 1)

    def test_tempo_formatado_em_minutos(self):
        desafio = Desafio.objects.create(
            titulo="Desafio 1 — Tempo",
            tipo_prova="ENADE",
            nivel=1,
            ordem=1,
            quantidade_questoes=5,
            tempo_total_segundos=600,
            ativo=True,
        )

        self.assertEqual(desafio.tempo_formatado, "10 min")

    def test_tempo_formatado_em_minutos_e_segundos(self):
        desafio = Desafio.objects.create(
            titulo="Desafio 1 — Tempo",
            tipo_prova="ENADE",
            nivel=1,
            ordem=1,
            quantidade_questoes=5,
            tempo_total_segundos=197,
            ativo=True,
        )

        self.assertEqual(desafio.tempo_formatado, "3 min e 17 seg")

    def test_tempo_formatado_em_segundos(self):
        desafio = Desafio.objects.create(
            titulo="Desafio 1 — Tempo",
            tipo_prova="ENADE",
            nivel=1,
            ordem=1,
            quantidade_questoes=1,
            tempo_total_segundos=45,
            ativo=True,
        )

        self.assertEqual(desafio.tempo_formatado, "45 seg")

    def test_nao_permite_mesma_ordem_para_mesmo_tipo_prova(self):
        Desafio.objects.create(
            titulo="Desafio 1",
            tipo_prova="ENADE",
            nivel=1,
            ordem=1,
            quantidade_questoes=5,
            tempo_total_segundos=600,
            ativo=True,
        )

        with self.assertRaises(IntegrityError):
            Desafio.objects.create(
                titulo="Desafio 1 Repetido",
                tipo_prova="ENADE",
                nivel=2,
                ordem=1,
                quantidade_questoes=5,
                tempo_total_segundos=600,
                ativo=True,
            )

    def test_permite_mesma_ordem_para_tipo_prova_diferente(self):
        Desafio.objects.create(
            titulo="Desafio ENADE",
            tipo_prova="ENADE",
            nivel=1,
            ordem=1,
            quantidade_questoes=5,
            tempo_total_segundos=600,
            ativo=True,
        )

        desafio_poscomp = Desafio.objects.create(
            titulo="Desafio POSCOMP",
            tipo_prova="POSCOMP",
            nivel=1,
            ordem=1,
            quantidade_questoes=5,
            tempo_total_segundos=600,
            ativo=True,
        )

        self.assertEqual(desafio_poscomp.ordem, 1)
        self.assertEqual(desafio_poscomp.tipo_prova, "POSCOMP")
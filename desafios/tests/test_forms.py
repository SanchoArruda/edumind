from django.test import TestCase

from desafios.forms import DesafioForm
from desafios.models import Desafio


class DesafioFormTest(TestCase):
    def test_desafio_form_valido(self):
        form = DesafioForm(data={
            "titulo": "Desafio 1 — Algoritmo",
            "tipo_prova": "ENADE",
            "nivel": 1,
            "ordem": 1,
            "quantidade_questoes": 5,
            "ativo": "on",
        })

        self.assertTrue(form.is_valid())

    def test_desafio_form_sem_titulo_invalido(self):
        form = DesafioForm(data={
            "titulo": "",
            "tipo_prova": "ENADE",
            "nivel": 1,
            "ordem": 1,
            "quantidade_questoes": 5,
            "ativo": "on",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("titulo", form.errors)

    def test_desafio_form_sem_tipo_prova_invalido(self):
        form = DesafioForm(data={
            "titulo": "Desafio 1",
            "tipo_prova": "",
            "nivel": 1,
            "ordem": 1,
            "quantidade_questoes": 5,
            "ativo": "on",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("tipo_prova", form.errors)

    def test_desafio_form_sem_quantidade_questoes_invalido(self):
        form = DesafioForm(data={
            "titulo": "Desafio 1",
            "tipo_prova": "ENADE",
            "nivel": 1,
            "ordem": 1,
            "quantidade_questoes": "",
            "ativo": "on",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("quantidade_questoes", form.errors)

    def test_desafio_form_nao_permite_mesma_ordem_para_mesmo_tipo(self):
        Desafio.objects.create(
            titulo="Desafio Existente",
            tipo_prova="ENADE",
            nivel=1,
            ordem=1,
            quantidade_questoes=5,
            tempo_total_segundos=600,
            ativo=True,
        )

        form = DesafioForm(data={
            "titulo": "Novo Desafio",
            "tipo_prova": "ENADE",
            "nivel": 2,
            "ordem": 1,
            "quantidade_questoes": 5,
            "ativo": "on",
        })

        self.assertFalse(form.is_valid())
        self.assertIn(
            "Já existe um desafio com essa ordem para este tipo de prova.",
            form.non_field_errors()
        )

    def test_desafio_form_permite_mesma_ordem_para_tipo_diferente(self):
        Desafio.objects.create(
            titulo="Desafio ENADE",
            tipo_prova="ENADE",
            nivel=1,
            ordem=1,
            quantidade_questoes=5,
            tempo_total_segundos=600,
            ativo=True,
        )

        form = DesafioForm(data={
            "titulo": "Desafio POSCOMP",
            "tipo_prova": "POSCOMP",
            "nivel": 1,
            "ordem": 1,
            "quantidade_questoes": 5,
            "ativo": "on",
        })

        self.assertTrue(form.is_valid())

    def test_desafio_form_edicao_permite_manter_mesma_ordem(self):
        desafio = Desafio.objects.create(
            titulo="Desafio Original",
            tipo_prova="ENADE",
            nivel=1,
            ordem=1,
            quantidade_questoes=5,
            tempo_total_segundos=600,
            ativo=True,
        )

        form = DesafioForm(
            data={
                "titulo": "Desafio Atualizado",
                "tipo_prova": "ENADE",
                "nivel": 2,
                "ordem": 1,
                "quantidade_questoes": 5,
                "ativo": "on",
            },
            instance=desafio,
        )

        self.assertTrue(form.is_valid())

    def test_tempo_total_formatado_inicial_em_edicao(self):
        desafio = Desafio.objects.create(
            titulo="Desafio Tempo",
            tipo_prova="ENADE",
            nivel=1,
            ordem=1,
            quantidade_questoes=5,
            tempo_total_segundos=197,
            ativo=True,
        )

        form = DesafioForm(instance=desafio)

        self.assertEqual(
            form.fields["tempo_total_formatado"].initial,
            "3 min e 17 seg"
        )
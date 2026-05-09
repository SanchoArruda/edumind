from django.test import TestCase

from disciplinas.forms import DisciplinaForm
from disciplinas.models import Disciplina


class DisciplinaFormTest(TestCase):

    def test_form_deve_ser_valido_com_nome(self):
        form = DisciplinaForm(data={
            "nome": "Banco de Dados"
        })

        self.assertTrue(form.is_valid())

    def test_form_deve_ser_invalido_sem_nome(self):
        form = DisciplinaForm(data={
            "nome": ""
        })

        self.assertFalse(form.is_valid())
        self.assertIn("nome", form.errors)

    def test_form_deve_remover_espacos_do_nome(self):
        form = DisciplinaForm(data={
            "nome": "  Banco de Dados  "
        })

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["nome"], "Banco de Dados")

    def test_form_deve_impedir_disciplina_com_nome_duplicado_ignorando_maiusculas(self):
        Disciplina.objects.create(nome="Banco de Dados")

        form = DisciplinaForm(data={
            "nome": "banco de dados"
        })

        self.assertFalse(form.is_valid())
        self.assertIn("nome", form.errors)
        self.assertEqual(
            form.errors["nome"][0],
            "Já existe uma disciplina com esse nome."
        )

    def test_form_deve_permitir_editar_disciplina_mantendo_o_mesmo_nome(self):
        disciplina = Disciplina.objects.create(nome="Banco de Dados")

        form = DisciplinaForm(
            data={
                "nome": "Banco de Dados"
            },
            instance=disciplina
        )

        self.assertTrue(form.is_valid())

    def test_form_deve_impedir_editar_para_nome_ja_existente(self):
        Disciplina.objects.create(nome="Banco de Dados")
        disciplina = Disciplina.objects.create(nome="Redes")

        form = DisciplinaForm(
            data={
                "nome": "Banco de Dados"
            },
            instance=disciplina
        )

        self.assertFalse(form.is_valid())
        self.assertIn("nome", form.errors)
        self.assertEqual(
            form.errors["nome"][0],
            "Já existe uma disciplina com esse nome."
        )

    def test_form_deve_ter_widget_com_classe_form_control(self):
        form = DisciplinaForm()

        self.assertEqual(
            form.fields["nome"].widget.attrs.get("class"),
            "form-control"
        )

    def test_form_deve_ter_placeholder(self):
        form = DisciplinaForm()

        self.assertEqual(
            form.fields["nome"].widget.attrs.get("placeholder"),
            "Digite o nome da disciplina"
        )
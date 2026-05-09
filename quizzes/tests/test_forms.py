from django.test import TestCase

from disciplinas.models import Disciplina
from quizzes.forms import QuestaoForm, QuizForm


class QuestaoFormTest(TestCase):
    def setUp(self):
        self.disciplina = Disciplina.objects.create(nome="Algoritmo")

    def dados_validos(self):
        return {
            "disciplina": self.disciplina.id,
            "tipo_prova": "ENADE",
            "nivel_dificuldade": "FACIL",
            "enunciado": "Quanto é 2 + 2?",
            "explicacao_resposta": "A resposta correta é 4.",
        }

    def test_questao_form_valido(self):
        form = QuestaoForm(data=self.dados_validos())

        self.assertTrue(form.is_valid())

    def test_questao_form_sem_disciplina_invalido(self):
        dados = self.dados_validos()
        dados["disciplina"] = ""

        form = QuestaoForm(data=dados)

        self.assertFalse(form.is_valid())
        self.assertIn("disciplina", form.errors)

    def test_questao_form_sem_tipo_prova_invalido(self):
        dados = self.dados_validos()
        dados["tipo_prova"] = ""

        form = QuestaoForm(data=dados)

        self.assertFalse(form.is_valid())
        self.assertIn("tipo_prova", form.errors)

    def test_questao_form_sem_nivel_dificuldade_invalido(self):
        dados = self.dados_validos()
        dados["nivel_dificuldade"] = ""

        form = QuestaoForm(data=dados)

        self.assertFalse(form.is_valid())
        self.assertIn("nivel_dificuldade", form.errors)

    def test_questao_form_sem_enunciado_invalido(self):
        dados = self.dados_validos()
        dados["enunciado"] = ""

        form = QuestaoForm(data=dados)

        self.assertFalse(form.is_valid())
        self.assertIn("enunciado", form.errors)

    def test_questao_form_sem_explicacao_resposta(self):
        dados = self.dados_validos()
        dados["explicacao_resposta"] = ""

        form = QuestaoForm(data=dados)

        # Se esse teste falhar, significa que explicacao_resposta é obrigatório no model.
        # Nesse caso, troque assertTrue por assertFalse e valide o erro.
        self.assertTrue(form.is_valid())

    def test_questao_form_com_tipo_prova_invalido(self):
        dados = self.dados_validos()
        dados["tipo_prova"] = "INVALIDO"

        form = QuestaoForm(data=dados)

        self.assertFalse(form.is_valid())
        self.assertIn("tipo_prova", form.errors)

    def test_questao_form_com_nivel_dificuldade_invalido(self):
        dados = self.dados_validos()
        dados["nivel_dificuldade"] = "INVALIDO"

        form = QuestaoForm(data=dados)

        self.assertFalse(form.is_valid())
        self.assertIn("nivel_dificuldade", form.errors)

    def test_questao_form_campos_esperados(self):
        form = QuestaoForm()

        self.assertEqual(
            list(form.fields.keys()),
            [
                "disciplina",
                "tipo_prova",
                "nivel_dificuldade",
                "enunciado",
                "explicacao_resposta",
            ]
        )

    def test_questao_form_labels(self):
        form = QuestaoForm()

        self.assertEqual(
            form.fields["disciplina"].label,
            "Área de Conhecimento / Disciplina"
        )
        self.assertEqual(form.fields["tipo_prova"].label, "Tipo de prova")
        self.assertEqual(
            form.fields["nivel_dificuldade"].label,
            "Nível de dificuldade"
        )
        self.assertEqual(form.fields["enunciado"].label, "Enunciado")
        self.assertEqual(form.fields["explicacao_resposta"].label, "Explicação")

    def test_questao_form_widgets_possuem_classe_form_control(self):
        form = QuestaoForm()

        self.assertEqual(
            form.fields["disciplina"].widget.attrs.get("class"),
            "form-control"
        )
        self.assertEqual(
            form.fields["tipo_prova"].widget.attrs.get("class"),
            "form-control"
        )
        self.assertEqual(
            form.fields["nivel_dificuldade"].widget.attrs.get("class"),
            "form-control"
        )
        self.assertEqual(
            form.fields["enunciado"].widget.attrs.get("class"),
            "form-control"
        )
        self.assertEqual(
            form.fields["explicacao_resposta"].widget.attrs.get("class"),
            "form-control"
        )

    def test_questao_form_widgets_textarea_possuem_rows(self):
        form = QuestaoForm()

        self.assertEqual(form.fields["enunciado"].widget.attrs.get("rows"), 4)
        self.assertEqual(
            form.fields["explicacao_resposta"].widget.attrs.get("rows"),
            4
        )

    def test_questao_form_placeholders(self):
        form = QuestaoForm()

        self.assertEqual(
            form.fields["enunciado"].widget.attrs.get("placeholder"),
            "Digite o enunciado da questão..."
        )
        self.assertEqual(
            form.fields["explicacao_resposta"].widget.attrs.get("placeholder"),
            "Explicação da resposta correta..."
        )


class QuizFormTest(TestCase):
    def setUp(self):
        self.disciplina = Disciplina.objects.create(nome="Banco de Dados")

    def dados_validos(self):
        return {
            "titulo": "Quiz de Banco de Dados",
            "descricao": "Quiz sobre conceitos básicos.",
            "disciplina": self.disciplina.id,
            "tipo_prova": "ENADE",
        }

    def test_quiz_form_valido(self):
        form = QuizForm(data=self.dados_validos())

        self.assertTrue(form.is_valid())

    def test_quiz_form_sem_titulo_invalido(self):
        dados = self.dados_validos()
        dados["titulo"] = ""

        form = QuizForm(data=dados)

        self.assertFalse(form.is_valid())
        self.assertIn("titulo", form.errors)

    def test_quiz_form_sem_descricao(self):
        dados = self.dados_validos()
        dados["descricao"] = ""

        form = QuizForm(data=dados)

        # Se esse teste falhar, significa que descricao é obrigatório no model.
        # Nesse caso, troque assertTrue por assertFalse.
        self.assertTrue(form.is_valid())

    def test_quiz_form_sem_disciplina_invalido(self):
        dados = self.dados_validos()
        dados["disciplina"] = ""

        form = QuizForm(data=dados)

        self.assertFalse(form.is_valid())
        self.assertIn("disciplina", form.errors)

    def test_quiz_form_sem_tipo_prova_invalido(self):
        dados = self.dados_validos()
        dados["tipo_prova"] = ""

        form = QuizForm(data=dados)

        self.assertFalse(form.is_valid())
        self.assertIn("tipo_prova", form.errors)

    def test_quiz_form_com_tipo_prova_invalido(self):
        dados = self.dados_validos()
        dados["tipo_prova"] = "INVALIDO"

        form = QuizForm(data=dados)

        self.assertFalse(form.is_valid())
        self.assertIn("tipo_prova", form.errors)

    def test_quiz_form_campos_esperados(self):
        form = QuizForm()

        self.assertEqual(
            list(form.fields.keys()),
            [
                "titulo",
                "descricao",
                "disciplina",
                "tipo_prova",
            ]
        )

    def test_quiz_form_labels(self):
        form = QuizForm()

        self.assertEqual(form.fields["titulo"].label, "Título")
        self.assertEqual(form.fields["descricao"].label, "Descrição")
        self.assertEqual(form.fields["disciplina"].label, "Disciplina / Área")
        self.assertEqual(form.fields["tipo_prova"].label, "Tipo da Prova")

    def test_quiz_form_widgets_possuem_classe_form_control(self):
        form = QuizForm()

        self.assertEqual(
            form.fields["titulo"].widget.attrs.get("class"),
            "form-control"
        )
        self.assertEqual(
            form.fields["descricao"].widget.attrs.get("class"),
            "form-control"
        )
        self.assertEqual(
            form.fields["disciplina"].widget.attrs.get("class"),
            "form-control"
        )
        self.assertEqual(
            form.fields["tipo_prova"].widget.attrs.get("class"),
            "form-control"
        )

    def test_quiz_form_descricao_possui_rows(self):
        form = QuizForm()

        self.assertEqual(form.fields["descricao"].widget.attrs.get("rows"), 4)

    def test_quiz_form_placeholders(self):
        form = QuizForm()

        self.assertEqual(
            form.fields["titulo"].widget.attrs.get("placeholder"),
            "Ex: Quiz de Banco de Dados"
        )
        self.assertEqual(
            form.fields["descricao"].widget.attrs.get("placeholder"),
            "Descreva o objetivo do quiz"
        )
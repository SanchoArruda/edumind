from django.test import TestCase
from django.urls import reverse

from disciplinas.models import Disciplina
from quizzes.models import Questao, Alternativa, Quiz, Tentativa
from usuarios.models import Usuario, TipoUsuario


class QuizViewsTest(TestCase):
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
            descricao="Quiz inicial.",
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

    def test_lista_quizzes_exige_login(self):
        response = self.client.get(reverse("quizzes:lista_quizzes"))

        self.assertEqual(response.status_code, 302)

    def test_estudante_acessa_lista_quizzes(self):
        self.client.login(username="estudante", password="123456")

        response = self.client.get(reverse("quizzes:lista_quizzes"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Quiz de Algoritmo")

    def test_filtro_quiz_por_busca(self):
        self.client.login(username="estudante", password="123456")

        response = self.client.get(
            reverse("quizzes:lista_quizzes"),
            {"q": "Algoritmo"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Quiz de Algoritmo")

    def test_iniciar_quiz_cria_tentativa(self):
        self.client.login(username="estudante", password="123456")

        response = self.client.get(
            reverse("quizzes:iniciar_quiz", args=[self.quiz.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Tentativa.objects.count(), 1)

        tentativa = Tentativa.objects.first()

        self.assertEqual(tentativa.usuario, self.estudante)
        self.assertEqual(tentativa.quiz, self.quiz)
        self.assertEqual(tentativa.tipo_tentativa, "QUIZ")
        self.assertFalse(tentativa.concluida)

    def test_responder_quiz_com_resposta_correta(self):
        self.client.login(username="estudante", password="123456")

        tentativa = Tentativa.objects.create(
            usuario=self.estudante,
            quiz=self.quiz,
            tipo_tentativa="QUIZ",
            concluida=False,
        )

        response = self.client.post(
            reverse("quizzes:responder_quiz", args=[tentativa.id]),
            {
                f"questao_{self.questao.id}": str(self.alternativa_correta.id),
                "tempo_gasto_segundos": "69",
            },
        )

        tentativa.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(tentativa.concluida)
        self.assertEqual(tentativa.quantidade_acertos, 1)
        self.assertEqual(tentativa.quantidade_erros, 0)
        self.assertEqual(tentativa.percentual_acertos, 100)
        self.assertEqual(tentativa.pontuacao, 5)
        self.assertEqual(tentativa.tempo_formatado, "1 min e 9 seg")

    def test_responder_quiz_com_resposta_errada(self):
        self.client.login(username="estudante", password="123456")

        tentativa = Tentativa.objects.create(
            usuario=self.estudante,
            quiz=self.quiz,
            tipo_tentativa="QUIZ",
            concluida=False,
        )

        response = self.client.post(
            reverse("quizzes:responder_quiz", args=[tentativa.id]),
            {
                f"questao_{self.questao.id}": str(self.alternativa_errada.id),
                "tempo_gasto_segundos": "7",
            },
        )

        tentativa.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(tentativa.concluida)
        self.assertEqual(tentativa.quantidade_acertos, 0)
        self.assertEqual(tentativa.quantidade_erros, 1)
        self.assertEqual(tentativa.percentual_acertos, 0)
        self.assertEqual(tentativa.pontuacao, 0)
        self.assertEqual(tentativa.tempo_formatado, "7 seg")

    def test_resultado_quiz_carrega(self):
        self.client.login(username="estudante", password="123456")

        tentativa = Tentativa.objects.create(
            usuario=self.estudante,
            quiz=self.quiz,
            tipo_tentativa="QUIZ",
            pontuacao=5,
            quantidade_acertos=1,
            quantidade_erros=0,
            percentual_acertos=100,
            desempenho_geral="Excelente desempenho!",
            concluida=True,
            respostas={str(self.questao.id): self.alternativa_correta.id},
        )

        response = self.client.get(
            reverse("quizzes:resultado_quiz", args=[tentativa.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Excelente desempenho!")
        self.assertContains(response, "Quiz de Algoritmo")

    def test_admin_acessa_lista_quizzes(self):
        self.client.login(username="admin", password="123456")

        response = self.client.get(reverse("quizzes:admin_lista_quizzes"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Quiz de Algoritmo")

    def test_estudante_nao_acessa_lista_admin_quizzes(self):
        self.client.login(username="estudante", password="123456")

        response = self.client.get(reverse("quizzes:admin_lista_quizzes"))

        self.assertEqual(response.status_code, 302)

    def test_admin_cria_quiz(self):
        self.client.login(username="admin", password="123456")

        response = self.client.post(
            reverse("quizzes:admin_criar_quiz"),
            {
                "titulo": "Novo Quiz",
                "descricao": "Descrição do novo quiz",
                "disciplina": self.disciplina.id,
                "tipo_prova": "POSCOMP",
                "questoes": [self.questao.id],
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Quiz.objects.filter(titulo="Novo Quiz").exists())

        quiz = Quiz.objects.get(titulo="Novo Quiz")

        self.assertEqual(quiz.questoes.count(), 1)

    def test_admin_cria_questao_geral(self):
        self.client.login(username="admin", password="123456")

        response = self.client.post(
            reverse("quizzes:admin_criar_questao_geral"),
            {
                "disciplina": self.disciplina.id,
                "tipo_prova": "ENADE",
                "nivel_dificuldade": "FACIL",
                "enunciado": "Nova questão de teste?",
                "explicacao_resposta": "Explicação da questão.",
                "letra[]": ["A", "B"],
                "texto[]": ["Resposta errada", "Resposta certa"],
                "correta": "B",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Questao.objects.filter(enunciado="Nova questão de teste?").exists()
        )

        questao = Questao.objects.get(enunciado="Nova questão de teste?")

        self.assertEqual(questao.alternativas.count(), 2)
        self.assertTrue(questao.alternativas.filter(correta=True).exists())

    def test_admin_exclui_quiz(self):
        self.client.login(username="admin", password="123456")

        response = self.client.post(
            reverse("quizzes:admin_excluir_quiz", args=[self.quiz.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Quiz.objects.filter(id=self.quiz.id).exists())



    def test_filtro_quiz_por_tipo_prova(self):
        self.client.login(username="estudante", password="123456")

        response = self.client.get(
            reverse("quizzes:lista_quizzes"),
            {"tipo_prova": "ENADE"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Quiz de Algoritmo")
        self.assertEqual(response.context["tipo_prova_selecionado"], "ENADE")

    def test_filtro_quiz_por_disciplina(self):
        self.client.login(username="estudante", password="123456")

        response = self.client.get(
            reverse("quizzes:lista_quizzes"),
            {"disciplina": str(self.disciplina.id)},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Quiz de Algoritmo")
        self.assertEqual(
            response.context["disciplina_selecionada"],
            str(self.disciplina.id),
        )

    def test_responder_quiz_get_carrega_template(self):
        self.client.login(username="estudante", password="123456")

        tentativa = Tentativa.objects.create(
            usuario=self.estudante,
            quiz=self.quiz,
            tipo_tentativa="QUIZ",
            concluida=False,
        )

        response = self.client.get(
            reverse("quizzes:responder_quiz", args=[tentativa.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "quizzes/estudante/responder_quiz.html"
        )
        self.assertEqual(response.context["quiz"], self.quiz)
        self.assertEqual(response.context["tentativa"], tentativa)
        self.assertEqual(response.context["total_questoes"], 1)

    def test_responder_quiz_concluido_redireciona_para_resultado(self):
        self.client.login(username="estudante", password="123456")

        tentativa = Tentativa.objects.create(
            usuario=self.estudante,
            quiz=self.quiz,
            tipo_tentativa="QUIZ",
            concluida=True,
        )

        response = self.client.get(
            reverse("quizzes:responder_quiz", args=[tentativa.id])
        )

        self.assertRedirects(
            response,
            reverse("quizzes:resultado_quiz", args=[tentativa.id])
        )

    def test_usuario_nao_acessa_tentativa_de_outro_usuario(self):
        outro_usuario = Usuario.objects.create_user(
            username="outro",
            nome="Outro Estudante",
            email="outro@email.com",
            password="123456",
            tipo_usuario=self.tipo_estudante,
        )

        tentativa = Tentativa.objects.create(
            usuario=outro_usuario,
            quiz=self.quiz,
            tipo_tentativa="QUIZ",
            concluida=False,
        )

        self.client.login(username="estudante", password="123456")

        response = self.client.get(
            reverse("quizzes:responder_quiz", args=[tentativa.id])
        )

        self.assertEqual(response.status_code, 404)

    def test_admin_acessa_formulario_criar_quiz(self):
        self.client.login(username="admin", password="123456")

        response = self.client.get(reverse("quizzes:admin_criar_quiz"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "quizzes/admin/admin_form_quiz.html"
        )
        self.assertIn("form", response.context)
        self.assertIn("questoes", response.context)
        self.assertEqual(response.context["questoes_marcadas"], set())

    def test_estudante_nao_acessa_criar_quiz_admin(self):
        self.client.login(username="estudante", password="123456")

        response = self.client.get(reverse("quizzes:admin_criar_quiz"))

        self.assertEqual(response.status_code, 302)

    def test_admin_acessa_lista_questoes_do_quiz(self):
        self.client.login(username="admin", password="123456")

        response = self.client.get(
            reverse("quizzes:admin_lista_questoes", args=[self.quiz.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "quizzes/admin/admin_lista_questoes.html"
        )
        self.assertEqual(response.context["quiz"], self.quiz)
        self.assertContains(response, "Quanto é 2 + 2?")

    def test_admin_acessa_todas_questoes(self):
        self.client.login(username="admin", password="123456")

        response = self.client.get(reverse("quizzes:admin_todas_questoes"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "quizzes/admin/admin_todas_questoes.html"
        )
        self.assertEqual(response.context["total_questoes"], 1)
        self.assertContains(response, "Quanto é 2 + 2?")

    def test_admin_acessa_formulario_criar_questao_geral(self):
        self.client.login(username="admin", password="123456")

        response = self.client.get(reverse("quizzes:admin_criar_questao_geral"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "quizzes/admin/admin_form_questao.html"
        )
        self.assertIn("form", response.context)
        self.assertEqual(response.context["letras"], ["A", "B", "C", "D"])

    def test_admin_nao_cria_questao_com_menos_de_duas_alternativas(self):
        self.client.login(username="admin", password="123456")

        response = self.client.post(
            reverse("quizzes:admin_criar_questao_geral"),
            {
                "disciplina": self.disciplina.id,
                "tipo_prova": "ENADE",
                "nivel_dificuldade": "FACIL",
                "enunciado": "Questão inválida?",
                "explicacao_resposta": "Explicação.",
                "letra[]": ["A"],
                "texto[]": ["Apenas uma alternativa"],
                "correta": "A",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Questao.objects.filter(enunciado="Questão inválida?").exists()
        )

    def test_admin_nao_cria_questao_com_mais_de_cinco_alternativas(self):
        self.client.login(username="admin", password="123456")

        response = self.client.post(
            reverse("quizzes:admin_criar_questao_geral"),
            {
                "disciplina": self.disciplina.id,
                "tipo_prova": "ENADE",
                "nivel_dificuldade": "FACIL",
                "enunciado": "Questão com muitas alternativas?",
                "explicacao_resposta": "Explicação.",
                "letra[]": ["A", "B", "C", "D", "E", "F"],
                "texto[]": ["A", "B", "C", "D", "E", "F"],
                "correta": "A",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Questao.objects.filter(
                enunciado="Questão com muitas alternativas?"
            ).exists()
        )

    def test_admin_nao_cria_questao_sem_alternativa_correta(self):
        self.client.login(username="admin", password="123456")

        response = self.client.post(
            reverse("quizzes:admin_criar_questao_geral"),
            {
                "disciplina": self.disciplina.id,
                "tipo_prova": "ENADE",
                "nivel_dificuldade": "FACIL",
                "enunciado": "Questão sem correta?",
                "explicacao_resposta": "Explicação.",
                "letra[]": ["A", "B"],
                "texto[]": ["Alternativa A", "Alternativa B"],
                "correta": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Questao.objects.filter(enunciado="Questão sem correta?").exists()
        )

    def test_admin_acessa_formulario_editar_questao(self):
        self.client.login(username="admin", password="123456")

        response = self.client.get(
            reverse("quizzes:admin_editar_questao", args=[self.questao.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "quizzes/admin/admin_form_questao.html"
        )
        self.assertEqual(response.context["questao"], self.questao)
        self.assertEqual(len(response.context["alternativas"]), 2)

    def test_admin_edita_questao(self):
        self.client.login(username="admin", password="123456")

        response = self.client.post(
            reverse("quizzes:admin_editar_questao", args=[self.questao.id]),
            {
                "disciplina": self.disciplina.id,
                "tipo_prova": "ENADE",
                "nivel_dificuldade": "FACIL",
                "enunciado": "Questão editada?",
                "explicacao_resposta": "Nova explicação.",
                "letra[]": ["A", "B"],
                "texto[]": ["Errada", "Correta"],
                "correta": "B",
            },
        )

        self.questao.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.questao.enunciado, "Questão editada?")
        self.assertEqual(self.questao.nivel_dificuldade, "FACIL")
        self.assertEqual(self.questao.alternativas.count(), 2)
        self.assertTrue(
            self.questao.alternativas.filter(
                letra="B",
                correta=True
            ).exists()
        )

    def test_admin_nao_edita_questao_com_menos_de_duas_alternativas(self):
        self.client.login(username="admin", password="123456")

        response = self.client.post(
            reverse("quizzes:admin_editar_questao", args=[self.questao.id]),
            {
                "disciplina": self.disciplina.id,
                "tipo_prova": "ENADE",
                "nivel_dificuldade": "FACIL",
                "enunciado": "Questão inválida editada?",
                "explicacao_resposta": "Explicação.",
                "letra[]": ["A"],
                "texto[]": ["Só uma"],
                "correta": "A",
            },
        )

        self.questao.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.questao.enunciado, "Quanto é 2 + 2?")

    def test_admin_exclui_questao(self):
        self.client.login(username="admin", password="123456")

        response = self.client.post(
            reverse("quizzes:admin_excluir_questao", args=[self.questao.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Questao.objects.filter(id=self.questao.id).exists())

    def test_get_excluir_questao_nao_exclui(self):
        self.client.login(username="admin", password="123456")

        response = self.client.get(
            reverse("quizzes:admin_excluir_questao", args=[self.questao.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Questao.objects.filter(id=self.questao.id).exists())

    def test_admin_acessa_formulario_editar_quiz(self):
        self.client.login(username="admin", password="123456")

        response = self.client.get(
            reverse("quizzes:admin_editar_quiz", args=[self.quiz.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "quizzes/admin/admin_form_quiz.html"
        )
        self.assertEqual(response.context["quiz"], self.quiz)
        self.assertIn(self.questao.id, response.context["questoes_marcadas"])

    def test_admin_edita_quiz(self):
        self.client.login(username="admin", password="123456")

        response = self.client.post(
            reverse("quizzes:admin_editar_quiz", args=[self.quiz.id]),
            {
                "titulo": "Quiz Editado",
                "descricao": "Descrição editada",
                "disciplina": self.disciplina.id,
                "tipo_prova": "POSCOMP",
                "questoes": [self.questao.id],
            },
        )

        self.quiz.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.quiz.titulo, "Quiz Editado")
        self.assertEqual(self.quiz.tipo_prova, "POSCOMP")
        self.assertEqual(self.quiz.questoes.count(), 1)

    def test_get_excluir_quiz_carrega_confirmacao(self):
        self.client.login(username="admin", password="123456")

        response = self.client.get(
            reverse("quizzes:admin_excluir_quiz", args=[self.quiz.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "quizzes/admin/admin_confirmar_exclusao_quiz.html"
        )
        self.assertEqual(response.context["quiz"], self.quiz)
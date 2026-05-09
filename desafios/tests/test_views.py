from django.test import TestCase
from django.urls import reverse

from desafios.models import Desafio
from disciplinas.models import Disciplina
from quizzes.models import Alternativa, Questao, Tentativa
from usuarios.models import TipoUsuario, Usuario


class DesafioViewsTest(TestCase):
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

        self.outro_estudante = Usuario.objects.create_user(
            username="outro_estudante",
            nome="Outro Estudante",
            email="outro@email.com",
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

        self.desafio_1 = Desafio.objects.create(
            titulo="Desafio 1 — Algoritmo",
            tipo_prova="ENADE",
            nivel=1,
            ordem=1,
            quantidade_questoes=2,
            tempo_total_segundos=600,
            ativo=True,
        )
        self.desafio_1.questoes.set([self.questao_1, self.questao_2])

        self.desafio_2 = Desafio.objects.create(
            titulo="Desafio 2 — Algoritmo",
            tipo_prova="ENADE",
            nivel=2,
            ordem=2,
            quantidade_questoes=2,
            tempo_total_segundos=600,
            ativo=True,
        )
        self.desafio_2.questoes.set([self.questao_1, self.questao_2])

    # -------------------------
    # Estudante - início
    # -------------------------

    def test_inicio_desafios_exige_login(self):
        response = self.client.get(reverse("desafios:inicio_desafios"))

        self.assertEqual(response.status_code, 302)

    def test_estudante_acessa_inicio_desafios(self):
        self.client.login(username="estudante", password="123456")

        response = self.client.get(reverse("desafios:inicio_desafios"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "desafios/estudante/inicio_desafios.html"
        )

    def test_admin_nao_acessa_inicio_desafios(self):
        self.client.login(username="admin", password="123456")

        response = self.client.get(reverse("desafios:inicio_desafios"))

        self.assertEqual(response.status_code, 302)

    # -------------------------
    # Estudante - lista
    # -------------------------

    def test_lista_desafios_exige_login(self):
        response = self.client.get(
            reverse("desafios:lista_desafios"),
            {"tipo_prova": "ENADE"},
        )

        self.assertEqual(response.status_code, 302)

    def test_admin_nao_acessa_lista_desafios_estudante(self):
        self.client.login(username="admin", password="123456")

        response = self.client.get(
            reverse("desafios:lista_desafios"),
            {"tipo_prova": "ENADE"},
        )

        self.assertEqual(response.status_code, 302)

    def test_lista_desafios_exige_tipo_prova_valido(self):
        self.client.login(username="estudante", password="123456")

        response = self.client.get(reverse("desafios:lista_desafios"))

        self.assertEqual(response.status_code, 302)

    def test_lista_desafios_redireciona_tipo_prova_invalido(self):
        self.client.login(username="estudante", password="123456")

        response = self.client.get(
            reverse("desafios:lista_desafios"),
            {"tipo_prova": "INVALIDO"},
        )

        self.assertEqual(response.status_code, 302)

    def test_estudante_acessa_lista_desafios_enade(self):
        self.client.login(username="estudante", password="123456")

        response = self.client.get(
            reverse("desafios:lista_desafios"),
            {"tipo_prova": "ENADE"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "desafios/estudante/lista_desafios.html"
        )
        self.assertContains(response, "Desafio 1")
        self.assertEqual(response.context["tipo_prova"], "ENADE")
        self.assertEqual(len(response.context["desafios_liberados"]), 2)

    def test_lista_desafios_marca_primeiro_liberado_e_segundo_bloqueado(self):
        self.client.login(username="estudante", password="123456")

        response = self.client.get(
            reverse("desafios:lista_desafios"),
            {"tipo_prova": "ENADE"},
        )

        desafios_liberados = response.context["desafios_liberados"]

        self.assertTrue(desafios_liberados[0]["liberado"])
        self.assertFalse(desafios_liberados[0]["concluido"])

        self.assertFalse(desafios_liberados[1]["liberado"])
        self.assertFalse(desafios_liberados[1]["concluido"])

    def test_lista_desafios_marca_desafio_concluido_e_proximo_liberado(self):
        Tentativa.objects.create(
            usuario=self.estudante,
            desafio=self.desafio_1,
            tipo_tentativa="DESAFIO",
            quantidade_acertos=2,
            quantidade_erros=0,
            percentual_acertos=100,
            pontuacao=5,
            concluida=True,
            aprovado=True,
        )

        self.client.login(username="estudante", password="123456")

        response = self.client.get(
            reverse("desafios:lista_desafios"),
            {"tipo_prova": "ENADE"},
        )

        desafios_liberados = response.context["desafios_liberados"]

        self.assertTrue(desafios_liberados[0]["liberado"])
        self.assertTrue(desafios_liberados[0]["concluido"])

        self.assertTrue(desafios_liberados[1]["liberado"])
        self.assertFalse(desafios_liberados[1]["concluido"])

    # -------------------------
    # Estudante - iniciar desafio
    # -------------------------

    def test_iniciar_desafio_exige_login(self):
        response = self.client.get(
            reverse("desafios:iniciar_desafio", args=[self.desafio_1.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Tentativa.objects.count(), 0)

    def test_admin_nao_inicia_desafio(self):
        self.client.login(username="admin", password="123456")

        response = self.client.get(
            reverse("desafios:iniciar_desafio", args=[self.desafio_1.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Tentativa.objects.count(), 0)

    def test_primeiro_desafio_pode_ser_iniciado(self):
        self.client.login(username="estudante", password="123456")

        response = self.client.get(
            reverse("desafios:iniciar_desafio", args=[self.desafio_1.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Tentativa.objects.count(), 1)

        tentativa = Tentativa.objects.first()

        self.assertEqual(tentativa.usuario, self.estudante)
        self.assertEqual(tentativa.desafio, self.desafio_1)
        self.assertEqual(tentativa.tipo_tentativa, "DESAFIO")
        self.assertFalse(tentativa.concluida)
        self.assertFalse(tentativa.aprovado)

    def test_segundo_desafio_bloqueado_sem_aprovar_primeiro(self):
        self.client.login(username="estudante", password="123456")

        response = self.client.get(
            reverse("desafios:iniciar_desafio", args=[self.desafio_2.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Tentativa.objects.count(), 0)

    def test_segundo_desafio_liberado_apos_aprovar_primeiro(self):
        Tentativa.objects.create(
            usuario=self.estudante,
            desafio=self.desafio_1,
            tipo_tentativa="DESAFIO",
            quantidade_acertos=2,
            quantidade_erros=0,
            percentual_acertos=100,
            pontuacao=5,
            concluida=True,
            aprovado=True,
        )

        self.client.login(username="estudante", password="123456")

        response = self.client.get(
            reverse("desafios:iniciar_desafio", args=[self.desafio_2.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Tentativa.objects.count(), 2)

        tentativa_nova = Tentativa.objects.order_by("-id").first()

        self.assertEqual(tentativa_nova.usuario, self.estudante)
        self.assertEqual(tentativa_nova.desafio, self.desafio_2)
        self.assertFalse(tentativa_nova.concluida)

    def test_nao_inicia_desafio_inativo(self):
        desafio_inativo = Desafio.objects.create(
            titulo="Desafio Inativo",
            tipo_prova="POSCOMP",
            nivel=1,
            ordem=1,
            quantidade_questoes=2,
            tempo_total_segundos=600,
            ativo=False,
        )

        self.client.login(username="estudante", password="123456")

        response = self.client.get(
            reverse("desafios:iniciar_desafio", args=[desafio_inativo.id])
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Tentativa.objects.count(), 0)

    # -------------------------
    # Estudante - responder desafio
    # -------------------------

    def test_responder_desafio_exige_login(self):
        tentativa = Tentativa.objects.create(
            usuario=self.estudante,
            desafio=self.desafio_1,
            tipo_tentativa="DESAFIO",
            concluida=False,
        )

        response = self.client.get(
            reverse("desafios:responder_desafio", args=[tentativa.id])
        )

        self.assertEqual(response.status_code, 302)

    def test_admin_nao_responde_desafio(self):
        tentativa = Tentativa.objects.create(
            usuario=self.estudante,
            desafio=self.desafio_1,
            tipo_tentativa="DESAFIO",
            concluida=False,
        )

        self.client.login(username="admin", password="123456")

        response = self.client.get(
            reverse("desafios:responder_desafio", args=[tentativa.id])
        )

        self.assertEqual(response.status_code, 302)

    def test_estudante_acessa_responder_desafio_get(self):
        tentativa = Tentativa.objects.create(
            usuario=self.estudante,
            desafio=self.desafio_1,
            tipo_tentativa="DESAFIO",
            concluida=False,
        )

        self.client.login(username="estudante", password="123456")

        response = self.client.get(
            reverse("desafios:responder_desafio", args=[tentativa.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "desafios/estudante/responder_desafio.html"
        )
        self.assertEqual(response.context["tentativa"], tentativa)
        self.assertEqual(response.context["desafio"], self.desafio_1)
        self.assertEqual(response.context["total_questoes"], 2)

    def test_responder_desafio_concluido_redireciona_para_resultado(self):
        tentativa = Tentativa.objects.create(
            usuario=self.estudante,
            desafio=self.desafio_1,
            tipo_tentativa="DESAFIO",
            concluida=True,
        )

        self.client.login(username="estudante", password="123456")

        response = self.client.get(
            reverse("desafios:responder_desafio", args=[tentativa.id])
        )

        self.assertRedirects(
            response,
            reverse("desafios:resultado_desafio", args=[tentativa.id])
        )

    def test_estudante_nao_acessa_tentativa_de_outro_usuario(self):
        tentativa = Tentativa.objects.create(
            usuario=self.outro_estudante,
            desafio=self.desafio_1,
            tipo_tentativa="DESAFIO",
            concluida=False,
        )

        self.client.login(username="estudante", password="123456")

        response = self.client.get(
            reverse("desafios:responder_desafio", args=[tentativa.id])
        )

        self.assertEqual(response.status_code, 404)

    def test_responder_desafio_com_aprovacao(self):
        tentativa = Tentativa.objects.create(
            usuario=self.estudante,
            desafio=self.desafio_1,
            tipo_tentativa="DESAFIO",
            concluida=False,
        )

        self.client.login(username="estudante", password="123456")

        response = self.client.post(
            reverse("desafios:responder_desafio", args=[tentativa.id]),
            {
                f"questao_{self.questao_1.id}": str(self.alternativa_1_correta.id),
                f"questao_{self.questao_2.id}": str(self.alternativa_2_correta.id),
                "tempo_gasto_segundos": "69",
            },
        )

        tentativa.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(tentativa.concluida)
        self.assertTrue(tentativa.aprovado)
        self.assertEqual(tentativa.quantidade_acertos, 2)
        self.assertEqual(tentativa.quantidade_erros, 0)
        self.assertEqual(tentativa.percentual_acertos, 100)
        self.assertEqual(tentativa.pontuacao, 5)
        self.assertEqual(tentativa.desempenho_geral, "Excelente desempenho!")
        self.assertEqual(tentativa.tempo_formatado, "1 min e 9 seg")

    def test_responder_desafio_sem_aprovacao(self):
        tentativa = Tentativa.objects.create(
            usuario=self.estudante,
            desafio=self.desafio_1,
            tipo_tentativa="DESAFIO",
            concluida=False,
        )

        self.client.login(username="estudante", password="123456")

        response = self.client.post(
            reverse("desafios:responder_desafio", args=[tentativa.id]),
            {
                f"questao_{self.questao_1.id}": str(self.alternativa_1_correta.id),
                f"questao_{self.questao_2.id}": str(self.alternativa_2_errada.id),
                "tempo_gasto_segundos": "30",
            },
        )

        tentativa.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(tentativa.concluida)
        self.assertFalse(tentativa.aprovado)
        self.assertEqual(tentativa.quantidade_acertos, 1)
        self.assertEqual(tentativa.quantidade_erros, 1)
        self.assertEqual(tentativa.percentual_acertos, 50)
        self.assertEqual(tentativa.pontuacao, 3)
        self.assertEqual(tentativa.desempenho_geral, "Bom esforço!")
        self.assertEqual(tentativa.tempo_formatado, "30 seg")

    def test_responder_desafio_sem_responder_questoes(self):
        tentativa = Tentativa.objects.create(
            usuario=self.estudante,
            desafio=self.desafio_1,
            tipo_tentativa="DESAFIO",
            concluida=False,
        )

        self.client.login(username="estudante", password="123456")

        response = self.client.post(
            reverse("desafios:responder_desafio", args=[tentativa.id]),
            {
                "tempo_gasto_segundos": "10",
            },
        )

        tentativa.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(tentativa.concluida)
        self.assertFalse(tentativa.aprovado)
        self.assertEqual(tentativa.quantidade_acertos, 0)
        self.assertEqual(tentativa.quantidade_erros, 2)
        self.assertEqual(tentativa.percentual_acertos, 0)
        self.assertEqual(tentativa.pontuacao, 0)
        self.assertEqual(tentativa.respostas, {})

    # -------------------------
    # Estudante - resultado desafio
    # -------------------------

    def test_resultado_desafio_exige_login(self):
        tentativa = Tentativa.objects.create(
            usuario=self.estudante,
            desafio=self.desafio_1,
            tipo_tentativa="DESAFIO",
            concluida=True,
        )

        response = self.client.get(
            reverse("desafios:resultado_desafio", args=[tentativa.id])
        )

        self.assertEqual(response.status_code, 302)

    def test_admin_nao_acessa_resultado_desafio(self):
        tentativa = Tentativa.objects.create(
            usuario=self.estudante,
            desafio=self.desafio_1,
            tipo_tentativa="DESAFIO",
            concluida=True,
        )

        self.client.login(username="admin", password="123456")

        response = self.client.get(
            reverse("desafios:resultado_desafio", args=[tentativa.id])
        )

        self.assertEqual(response.status_code, 302)

    def test_resultado_desafio_carrega(self):
        tentativa = Tentativa.objects.create(
            usuario=self.estudante,
            desafio=self.desafio_1,
            tipo_tentativa="DESAFIO",
            quantidade_acertos=2,
            quantidade_erros=0,
            percentual_acertos=100,
            pontuacao=5,
            desempenho_geral="Excelente desempenho!",
            concluida=True,
            aprovado=True,
            respostas={
                str(self.questao_1.id): self.alternativa_1_correta.id,
                str(self.questao_2.id): self.alternativa_2_correta.id,
            },
        )

        self.client.login(username="estudante", password="123456")

        response = self.client.get(
            reverse("desafios:resultado_desafio", args=[tentativa.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "desafios/estudante/resultado_desafio.html"
        )
        self.assertContains(response, "Excelente desempenho!")
        self.assertContains(response, "Desafio 1")
        self.assertEqual(response.context["estrelas"], 5)
        self.assertEqual(response.context["emoji_resultado"], "🏆")
        self.assertEqual(response.context["proximo_desafio"], self.desafio_2)
        self.assertEqual(len(response.context["revisao_questoes"]), 2)

    def test_resultado_desafio_de_outro_usuario_retorna_404(self):
        tentativa = Tentativa.objects.create(
            usuario=self.outro_estudante,
            desafio=self.desafio_1,
            tipo_tentativa="DESAFIO",
            quantidade_acertos=2,
            quantidade_erros=0,
            percentual_acertos=100,
            pontuacao=5,
            concluida=True,
            aprovado=True,
        )

        self.client.login(username="estudante", password="123456")

        response = self.client.get(
            reverse("desafios:resultado_desafio", args=[tentativa.id])
        )

        self.assertEqual(response.status_code, 404)

    def test_resultado_desafio_sem_questoes_respondidas(self):
        tentativa = Tentativa.objects.create(
            usuario=self.estudante,
            desafio=self.desafio_1,
            tipo_tentativa="DESAFIO",
            quantidade_acertos=0,
            quantidade_erros=0,
            percentual_acertos=0,
            pontuacao=0,
            desempenho_geral="",
            concluida=True,
            aprovado=False,
            respostas={},
        )

        self.client.login(username="estudante", password="123456")

        response = self.client.get(
            reverse("desafios:resultado_desafio", args=[tentativa.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["percentual_acertos"], 0)
        self.assertEqual(response.context["estrelas"], 0)
        self.assertEqual(response.context["emoji_resultado"], "📚")

    # -------------------------
    # Admin - lista desafios
    # -------------------------

    def test_admin_lista_desafios_exige_login(self):
        response = self.client.get(reverse("desafios:admin_lista_desafios"))

        self.assertEqual(response.status_code, 302)

    def test_admin_acessa_lista_desafios(self):
        self.client.login(username="admin", password="123456")

        response = self.client.get(reverse("desafios:admin_lista_desafios"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "desafios/admin/admin_lista_desafios.html"
        )
        self.assertContains(response, "Desafio 1")
        self.assertEqual(response.context["total_desafios"], 2)

    def test_admin_filtra_lista_desafios_por_tipo(self):
        Desafio.objects.create(
            titulo="Desafio POSCOMP",
            tipo_prova="POSCOMP",
            nivel=1,
            ordem=1,
            quantidade_questoes=2,
            tempo_total_segundos=600,
            ativo=True,
        )

        self.client.login(username="admin", password="123456")

        response = self.client.get(
            reverse("desafios:admin_lista_desafios"),
            {"tipo": "POSCOMP"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["filtro_tipo"], "POSCOMP")
        self.assertEqual(response.context["total_desafios"], 1)
        self.assertContains(response, "Desafio POSCOMP")

    def test_admin_lista_desafios_ignora_filtro_invalido(self):
        self.client.login(username="admin", password="123456")

        response = self.client.get(
            reverse("desafios:admin_lista_desafios"),
            {"tipo": "INVALIDO"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["filtro_tipo"], "INVALIDO")
        self.assertEqual(response.context["total_desafios"], 2)

    def test_estudante_nao_acessa_lista_admin_desafios(self):
        self.client.login(username="estudante", password="123456")

        response = self.client.get(reverse("desafios:admin_lista_desafios"))

        self.assertEqual(response.status_code, 302)

    # -------------------------
    # Admin - criar desafio
    # -------------------------

    def test_admin_acessa_formulario_criar_desafio(self):
        self.client.login(username="admin", password="123456")

        response = self.client.get(reverse("desafios:admin_criar_desafio"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "desafios/admin/admin_form_desafio.html"
        )
        self.assertIn("form", response.context)
        self.assertIn("questoes", response.context)
        self.assertEqual(response.context["questoes_marcadas"], set())

    def test_estudante_nao_acessa_criar_desafio_admin(self):
        self.client.login(username="estudante", password="123456")

        response = self.client.get(reverse("desafios:admin_criar_desafio"))

        self.assertEqual(response.status_code, 302)

    def test_admin_cria_desafio(self):
        self.client.login(username="admin", password="123456")

        response = self.client.post(
            reverse("desafios:admin_criar_desafio"),
            {
                "titulo": "Desafio 1 — POSCOMP",
                "tipo_prova": "POSCOMP",
                "nivel": 1,
                "ordem": 1,
                "quantidade_questoes": 2,
                "ativo": "on",
                "tempo_total_segundos": 600,
                "questoes": [self.questao_1.id, self.questao_2.id],
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Desafio.objects.filter(titulo="Desafio 1 — POSCOMP").exists()
        )

        desafio = Desafio.objects.get(titulo="Desafio 1 — POSCOMP")

        self.assertEqual(desafio.questoes.count(), 2)
        self.assertEqual(desafio.tempo_total_segundos, 600)
        self.assertEqual(desafio.tempo_formatado, "10 min")

    def test_admin_cria_desafio_sem_questoes(self):
        self.client.login(username="admin", password="123456")

        response = self.client.post(
            reverse("desafios:admin_criar_desafio"),
            {
                "titulo": "Desafio Sem Questões",
                "tipo_prova": "POSCOMP",
                "nivel": 1,
                "ordem": 1,
                "quantidade_questoes": 2,
                "ativo": "on",
                "tempo_total_segundos": 300,
            },
        )

        self.assertEqual(response.status_code, 302)

        desafio = Desafio.objects.get(titulo="Desafio Sem Questões")

        self.assertEqual(desafio.questoes.count(), 0)
        self.assertEqual(desafio.tempo_total_segundos, 300)

    def test_admin_nao_cria_desafio_com_formulario_invalido(self):
        self.client.login(username="admin", password="123456")

        response = self.client.post(
            reverse("desafios:admin_criar_desafio"),
            {
                "titulo": "",
                "tipo_prova": "POSCOMP",
                "nivel": 1,
                "ordem": 1,
                "quantidade_questoes": 2,
                "ativo": "on",
                "tempo_total_segundos": 600,
                "questoes": [self.questao_1.id],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Desafio.objects.filter(tipo_prova="POSCOMP").exists())
        self.assertIn("form", response.context)
        self.assertIn("titulo", response.context["form"].errors)

    # -------------------------
    # Admin - editar desafio
    # -------------------------

    def test_admin_acessa_formulario_editar_desafio(self):
        self.client.login(username="admin", password="123456")

        response = self.client.get(
            reverse("desafios:admin_editar_desafio", args=[self.desafio_1.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "desafios/admin/admin_form_desafio.html"
        )
        self.assertEqual(response.context["desafio"], self.desafio_1)
        self.assertIn(self.questao_1.id, response.context["questoes_marcadas"])
        self.assertIn(self.questao_2.id, response.context["questoes_marcadas"])

    def test_estudante_nao_acessa_editar_desafio_admin(self):
        self.client.login(username="estudante", password="123456")

        response = self.client.get(
            reverse("desafios:admin_editar_desafio", args=[self.desafio_1.id])
        )

        self.assertEqual(response.status_code, 302)

    def test_admin_edita_desafio(self):
        self.client.login(username="admin", password="123456")

        response = self.client.post(
            reverse("desafios:admin_editar_desafio", args=[self.desafio_1.id]),
            {
                "titulo": "Desafio 1 — Atualizado",
                "tipo_prova": "ENADE",
                "nivel": 2,
                "ordem": 1,
                "quantidade_questoes": 2,
                "ativo": "on",
                "tempo_total_segundos": 900,
                "questoes": [self.questao_1.id],
            },
        )

        self.desafio_1.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.desafio_1.titulo, "Desafio 1 — Atualizado")
        self.assertEqual(self.desafio_1.nivel, 2)
        self.assertEqual(self.desafio_1.tempo_total_segundos, 900)
        self.assertEqual(self.desafio_1.questoes.count(), 1)
        self.assertIn(self.questao_1, self.desafio_1.questoes.all())

    def test_admin_edita_desafio_removendo_questoes(self):
        self.client.login(username="admin", password="123456")

        response = self.client.post(
            reverse("desafios:admin_editar_desafio", args=[self.desafio_1.id]),
            {
                "titulo": "Desafio Sem Questões Depois",
                "tipo_prova": "ENADE",
                "nivel": 1,
                "ordem": 1,
                "quantidade_questoes": 2,
                "ativo": "on",
                "tempo_total_segundos": 600,
            },
        )

        self.desafio_1.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.desafio_1.titulo, "Desafio Sem Questões Depois")
        self.assertEqual(self.desafio_1.questoes.count(), 0)

    def test_admin_nao_edita_desafio_com_formulario_invalido(self):
        self.client.login(username="admin", password="123456")

        response = self.client.post(
            reverse("desafios:admin_editar_desafio", args=[self.desafio_1.id]),
            {
                "titulo": "",
                "tipo_prova": "ENADE",
                "nivel": 1,
                "ordem": 1,
                "quantidade_questoes": 2,
                "ativo": "on",
                "tempo_total_segundos": 600,
                "questoes": [self.questao_1.id],
            },
        )

        self.desafio_1.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.desafio_1.titulo, "Desafio 1 — Algoritmo")
        self.assertIn("form", response.context)
        self.assertIn("titulo", response.context["form"].errors)

    def test_admin_nao_edita_desafio_para_ordem_duplicada_no_mesmo_tipo(self):
        self.client.login(username="admin", password="123456")

        response = self.client.post(
            reverse("desafios:admin_editar_desafio", args=[self.desafio_2.id]),
            {
                "titulo": "Desafio 2 — Ordem Duplicada",
                "tipo_prova": "ENADE",
                "nivel": 2,
                "ordem": 1,
                "quantidade_questoes": 2,
                "ativo": "on",
                "tempo_total_segundos": 600,
                "questoes": [self.questao_1.id],
            },
        )

        self.desafio_2.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.desafio_2.ordem, 2)
        self.assertIn(
            "Já existe um desafio com essa ordem para este tipo de prova.",
            response.context["form"].non_field_errors()
        )

    # -------------------------
    # Admin - excluir desafio
    # -------------------------

    def test_admin_acessa_confirmacao_excluir_desafio(self):
        self.client.login(username="admin", password="123456")

        response = self.client.get(
            reverse("desafios:admin_excluir_desafio", args=[self.desafio_2.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "desafios/admin/admin_confirmar_exclusao_desafio.html"
        )
        self.assertEqual(response.context["desafio"], self.desafio_2)
        self.assertTrue(Desafio.objects.filter(id=self.desafio_2.id).exists())

    def test_estudante_nao_acessa_excluir_desafio_admin(self):
        self.client.login(username="estudante", password="123456")

        response = self.client.get(
            reverse("desafios:admin_excluir_desafio", args=[self.desafio_2.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Desafio.objects.filter(id=self.desafio_2.id).exists())

    def test_admin_exclui_desafio(self):
        self.client.login(username="admin", password="123456")

        response = self.client.post(
            reverse("desafios:admin_excluir_desafio", args=[self.desafio_2.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Desafio.objects.filter(id=self.desafio_2.id).exists()
        )
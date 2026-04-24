from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from disciplinas.models import Disciplina
from .models import Quiz, Questao, Alternativa, TentativaQuiz

from .utils import calcular_xp_tentativa

def usuario_e_admin(user):
    return (
        user.is_authenticated
        and user.tipo_usuario
        and user.tipo_usuario.perfil.lower() == "administrador"
    )


@login_required
def lista_quizzes(request):
    quizzes = Quiz.objects.select_related("disciplina").prefetch_related("questoes").all()

    tipo_prova = request.GET.get("tipo_prova")
    disciplina_id = request.GET.get("disciplina")

    if tipo_prova:
        quizzes = quizzes.filter(tipo_prova=tipo_prova)

    if disciplina_id:
        quizzes = quizzes.filter(disciplina_id=disciplina_id)

    disciplinas = Disciplina.objects.all()

    contexto = {
        "quizzes": quizzes,
        "disciplinas": disciplinas,
        "tipos_prova": Quiz.TIPO_PROVA_CHOICES,
        "tipo_prova_selecionado": tipo_prova,
        "disciplina_selecionada": disciplina_id,
    }

    return render(request, "quizzes/estudante/lista_quizzes.html", contexto)


@login_required
def responder_quiz(request, quiz_id):
    quiz = get_object_or_404(
        Quiz.objects.select_related("disciplina").prefetch_related("questoes__alternativas"),
        id=quiz_id
    )

    questoes = quiz.questoes.all()

    if request.method == "POST":
        quantidade_acertos = 0
        quantidade_erros = 0
        total_questoes = questoes.count()

        for questao in questoes:
            alternativa_id = request.POST.get(f"questao_{questao.id}")

            if alternativa_id:
                alternativa = Alternativa.objects.filter(
                    id=alternativa_id,
                    questao=questao
                ).first()

                if alternativa and alternativa.correta:
                    quantidade_acertos += 1
                else:
                    quantidade_erros += 1
            else:
                quantidade_erros += 1

        percentual_acertos = 0
        if total_questoes > 0:
            percentual_acertos = round((quantidade_acertos / total_questoes) * 100, 2)

        pontuacao = calcular_xp_tentativa(quantidade_acertos)

        if percentual_acertos >= 80:
            desempenho_geral = "Excelente"
        elif percentual_acertos >= 60:
            desempenho_geral = "Bom"
        elif percentual_acertos >= 40:
            desempenho_geral = "Regular"
        else:
            desempenho_geral = "Precisa melhorar"

        tentativa = TentativaQuiz.objects.create(
            usuario=request.user,
            quiz=quiz,
            pontuacao=pontuacao,
            quantidade_acertos=quantidade_acertos,
            quantidade_erros=quantidade_erros,
            percentual_acertos=percentual_acertos,
            desempenho_geral=desempenho_geral,
            concluida=True,
        )

        return redirect("quizzes:resultado_quiz", tentativa_id=tentativa.id)

    contexto = {
        "quiz": quiz,
        "questoes": questoes,
    }

    return render(request, "quizzes/estudante/responder_quiz.html", contexto)


@login_required
def resultado_quiz(request, tentativa_id):
    tentativa = get_object_or_404(
        TentativaQuiz.objects.select_related("quiz", "quiz__disciplina", "usuario"),
        id=tentativa_id,
        usuario=request.user
    )

    contexto = {
        "tentativa": tentativa
    }

    return render(request, "quizzes/estudante/resultado_quiz.html", contexto)


# ---------------------------------
# PARTE DO ADMIN
# ---------------------------------

@login_required
def admin_lista_quizzes(request):
    if not usuario_e_admin(request.user):
        return redirect("login")

    quizzes = Quiz.objects.select_related("disciplina").prefetch_related("questoes").all()

    contexto = {
        "quizzes": quizzes
    }

    return render(request, "quizzes/admin/admin_lista_quizzes.html", contexto)


@login_required
def admin_criar_quiz(request):
    if not usuario_e_admin(request.user):
        return redirect("login")

    disciplinas = Disciplina.objects.all()
    questoes = Questao.objects.select_related("disciplina").all()

    if request.method == "POST":
        titulo = request.POST.get("titulo")
        descricao = request.POST.get("descricao")
        disciplina_id = request.POST.get("disciplina")
        questoes_ids = request.POST.getlist("questoes")
        tipo_prova = request.POST.get("tipo_prova")

        if not titulo or not disciplina_id:
            messages.error(request, "Preencha o título e a disciplina.")
            return redirect("quizzes:admin_criar_quiz")

        disciplina = get_object_or_404(Disciplina, id=disciplina_id)

        quiz = Quiz.objects.create(
            titulo=titulo,
            descricao=descricao,
            disciplina=disciplina,
            tipo_prova=tipo_prova
        )

        if questoes_ids:
            questoes_selecionadas = Questao.objects.filter(
                id__in=questoes_ids,
                disciplina=disciplina
            )
            quiz.questoes.set(questoes_selecionadas)

        messages.success(request, "Quiz criado com sucesso.")
        return redirect("quizzes:admin_lista_quizzes")

    contexto = {
        "disciplinas": disciplinas,
        "questoes": questoes,
        "tipos_prova": Quiz.TIPO_PROVA_CHOICES,
    }

    return render(request, "quizzes/admin/admin_criar_quiz.html", contexto)


@login_required
def admin_lista_questoes(request, quiz_id):
    if not usuario_e_admin(request.user):
        return redirect("login")

    quiz = get_object_or_404(
        Quiz.objects.select_related("disciplina").prefetch_related("questoes__alternativas"),
        id=quiz_id
    )

    contexto = {
        "quiz": quiz,
        "questoes": quiz.questoes.all()
    }

    return render(request, "quizzes/admin/admin_lista_questoes.html", contexto)


@login_required
def admin_criar_questao(request, quiz_id):
    if not usuario_e_admin(request.user):
        return redirect("login")

    quiz = get_object_or_404(
        Quiz.objects.select_related("disciplina"),
        id=quiz_id
    )

    if request.method == "POST":
        enunciado = request.POST.get("enunciado")
        explicacao_resposta = request.POST.get("explicacao_resposta")

        letras = request.POST.getlist("letra[]")
        textos = request.POST.getlist("texto[]")
        correta = request.POST.get("correta")

        if not enunciado:
            messages.error(request, "Informe o enunciado da questão.")
            return redirect("quizzes:admin_criar_questao", quiz_id=quiz.id)

        alternativas_validas = [texto for texto in textos if texto.strip()]

        if len(alternativas_validas) < 2:
            messages.error(request, "Cadastre pelo menos duas alternativas.")
            return redirect("quizzes:admin_criar_questao", quiz_id=quiz.id)

        if len(alternativas_validas) > 5:
            messages.error(request, "Cadastre no máximo cinco alternativas.")
            return redirect("quizzes:admin_criar_questao", quiz_id=quiz.id)

        if not correta:
            messages.error(request, "Marque uma alternativa correta.")
            return redirect("quizzes:admin_criar_questao", quiz_id=quiz.id)

        questao = Questao.objects.create(
            disciplina=quiz.disciplina,
            enunciado=enunciado,
            explicacao_resposta=explicacao_resposta
        )

        quiz.questoes.add(questao)

        for letra, texto in zip(letras, textos):
            if texto.strip():
                Alternativa.objects.create(
                    questao=questao,
                    letra=letra,
                    texto=texto,
                    correta=(letra == correta)
                )

        messages.success(request, "Questão cadastrada com sucesso.")
        return redirect("quizzes:admin_lista_questoes", quiz_id=quiz.id)

    contexto = {
        "quiz": quiz,
        "letras": ["A", "B", "C", "D"],
    }

    return render(request, "quizzes/admin/admin_criar_questao.html", contexto)


@login_required
def admin_todas_questoes(request):
    if not usuario_e_admin(request.user):
        return redirect("login")

    questoes = Questao.objects.select_related(
        "disciplina"
    ).prefetch_related(
        "alternativas",
        "quizzes"
    ).all().order_by("-id")

    contexto = {
        "questoes": questoes,
        "total_questoes": questoes.count(),
    }

    return render(request, "quizzes/admin/admin_todas_questoes.html", contexto)


@login_required
def admin_criar_questao_geral(request):
    if not usuario_e_admin(request.user):
        return redirect("login")

    disciplinas = Disciplina.objects.all()

    if request.method == "POST":
        disciplina_id = request.POST.get("disciplina")
        enunciado = request.POST.get("enunciado")
        explicacao_resposta = request.POST.get("explicacao_resposta")

        letras = request.POST.getlist("letra[]")
        textos = request.POST.getlist("texto[]")
        correta = request.POST.get("correta")

        if not disciplina_id:
            messages.error(request, "Selecione a disciplina da questão.")
            return redirect("quizzes:admin_criar_questao_geral")

        if not enunciado:
            messages.error(request, "Informe o enunciado da questão.")
            return redirect("quizzes:admin_criar_questao_geral")

        alternativas_validas = [texto for texto in textos if texto.strip()]

        if len(alternativas_validas) < 2:
            messages.error(request, "Cadastre pelo menos duas alternativas.")
            return redirect("quizzes:admin_criar_questao_geral")

        if not correta:
            messages.error(request, "Marque uma alternativa correta.")
            return redirect("quizzes:admin_criar_questao_geral")

        disciplina = get_object_or_404(Disciplina, id=disciplina_id)

        questao = Questao.objects.create(
            disciplina=disciplina,
            enunciado=enunciado,
            explicacao_resposta=explicacao_resposta
        )

        for letra, texto in zip(letras, textos):
            if texto.strip():
                Alternativa.objects.create(
                    questao=questao,
                    letra=letra,
                    texto=texto,
                    correta=(letra == correta)
                )

        messages.success(request, "Questão cadastrada com sucesso.")
        return redirect("quizzes:admin_todas_questoes")

    contexto = {
        "disciplinas": disciplinas,
        "letras": ["A", "B", "C", "D"],
    }

    return render(request, "quizzes/admin/admin_form_questao.html", contexto)


@login_required
def admin_editar_questao(request, questao_id):
    if not usuario_e_admin(request.user):
        return redirect("login")

    questao = get_object_or_404(
        Questao.objects.select_related("disciplina").prefetch_related("alternativas"),
        id=questao_id
    )

    disciplinas = Disciplina.objects.all()
    alternativas = list(questao.alternativas.all().order_by("letra"))

    if request.method == "POST":
        disciplina_id = request.POST.get("disciplina")
        enunciado = request.POST.get("enunciado")
        explicacao_resposta = request.POST.get("explicacao_resposta")

        letras = request.POST.getlist("letra[]")
        textos = request.POST.getlist("texto[]")
        correta = request.POST.get("correta")

        if not disciplina_id:
            messages.error(request, "Selecione a disciplina da questão.")
            return redirect("quizzes:admin_editar_questao", questao_id=questao.id)

        if not enunciado:
            messages.error(request, "Informe o enunciado da questão.")
            return redirect("quizzes:admin_editar_questao", questao_id=questao.id)

        alternativas_validas = [texto for texto in textos if texto.strip()]

        if len(alternativas_validas) < 2:
            messages.error(request, "Cadastre pelo menos duas alternativas.")
            return redirect("quizzes:admin_editar_questao", questao_id=questao.id)

        if len(alternativas_validas) > 5:
            messages.error(request, "Cadastre no máximo cinco alternativas.")
            return redirect("quizzes:admin_editar_questao", questao_id=questao.id)

        if not correta:
            messages.error(request, "Marque uma alternativa correta.")
            return redirect("quizzes:admin_editar_questao", questao_id=questao.id)
        
        disciplina = get_object_or_404(Disciplina, id=disciplina_id)

        questao.disciplina = disciplina
        questao.enunciado = enunciado
        questao.explicacao_resposta = explicacao_resposta
        questao.save()

        questao.alternativas.all().delete()

        for letra, texto in zip(letras, textos):
            if texto.strip():
                Alternativa.objects.create(
                    questao=questao,
                    letra=letra,
                    texto=texto,
                    correta=(letra == correta)
                )

        messages.success(request, "Questão atualizada com sucesso.")
        return redirect("quizzes:admin_todas_questoes")

    contexto = {
        "questao": questao,
        "disciplinas": disciplinas,
        "alternativas": alternativas,
        "letras": ["A", "B", "C", "D"],
    }

    return render(request, "quizzes/admin/admin_form_questao.html", contexto)


@login_required
def admin_excluir_questao(request, questao_id):
    if not usuario_e_admin(request.user):
        return redirect("login")

    questao = get_object_or_404(Questao, id=questao_id)

    if request.method == "POST":
        questao.delete()
        messages.success(request, "Questão excluída com sucesso.")
        return redirect("quizzes:admin_todas_questoes")

    return redirect("quizzes:admin_todas_questoes")
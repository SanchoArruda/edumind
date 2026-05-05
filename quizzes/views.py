from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from disciplinas.models import Disciplina
from .models import Quiz, Questao, Alternativa, Tentativa
from .utils import calcular_xp_tentativa

from .forms import QuestaoForm, QuizForm


def usuario_e_admin(user):
    return (
        user.is_authenticated
        and user.tipo_usuario
        and user.tipo_usuario.perfil.lower() == "administrador"
    )


@login_required
def lista_quizzes(request):
    quizzes = Quiz.objects.select_related("disciplina").prefetch_related("questoes").all()

    q = request.GET.get("q", "").strip()
    tipo_prova = request.GET.get("tipo_prova", "").strip()
    disciplina_id = request.GET.get("disciplina", "").strip()

    if q:
        quizzes = quizzes.filter(
            Q(titulo__icontains=q) |
            Q(descricao__icontains=q) |
            Q(disciplina__nome__icontains=q) |
            Q(tipo_prova__icontains=q)
        )

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
        "q": q,
    }

    return render(request, "quizzes/estudante/lista_quizzes.html", contexto)


@login_required
def iniciar_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    tentativa = Tentativa.objects.create(
        usuario=request.user,
        quiz=quiz,
        tipo_tentativa="QUIZ",
        pontuacao=0,
        quantidade_acertos=0,
        quantidade_erros=0,
        percentual_acertos=0,
        desempenho_geral="",
        concluida=False,
        aprovado=False,
    )

    return redirect("quizzes:responder_quiz", tentativa_id=tentativa.id)


@login_required
def responder_quiz(request, tentativa_id):
    tentativa = get_object_or_404(
        Tentativa.objects.select_related("quiz", "quiz__disciplina", "usuario")
        .prefetch_related("quiz__questoes__alternativas"),
        id=tentativa_id,
        usuario=request.user,
        tipo_tentativa="QUIZ",
    )

    if tentativa.concluida:
        return redirect("quizzes:resultado_quiz", tentativa_id=tentativa.id)

    quiz = tentativa.quiz
    questoes = quiz.questoes.all()
    total_questoes = questoes.count()

    if request.method == "POST":
        quantidade_acertos = 0
        quantidade_erros = 0
        respostas_usuario = {}

        for questao in questoes:
            alternativa_id = request.POST.get(f"questao_{questao.id}")

            if alternativa_id:
                respostas_usuario[str(questao.id)] = int(alternativa_id)

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

        if percentual_acertos == 100:
            desempenho_geral = "Excelente desempenho!"
        elif percentual_acertos >= 70:
            desempenho_geral = "Muito bem! Continue assim!"
        elif percentual_acertos >= 40:
            desempenho_geral = "Bom esforço! Continue praticando!"
        else:
            desempenho_geral = "Continue praticando!"

        tempo_gasto_segundos = int(request.POST.get("tempo_gasto_segundos", 0) or 0)

        tentativa.respostas = respostas_usuario
        tentativa.pontuacao = pontuacao
        tentativa.quantidade_acertos = quantidade_acertos
        tentativa.quantidade_erros = quantidade_erros
        tentativa.percentual_acertos = percentual_acertos
        tentativa.desempenho_geral = desempenho_geral
        tentativa.tempo_gasto = timedelta(seconds=tempo_gasto_segundos)
        tentativa.concluida = True
        tentativa.aprovado = False
        tentativa.save()

        return redirect("quizzes:resultado_quiz", tentativa_id=tentativa.id)

    contexto = {
        "quiz": quiz,
        "questoes": questoes,
        "tentativa": tentativa,
        "total_questoes": total_questoes,
    }

    return render(request, "quizzes/estudante/responder_quiz.html", contexto)


@login_required
def resultado_quiz(request, tentativa_id):
    tentativa = get_object_or_404(
        Tentativa.objects.select_related("quiz", "quiz__disciplina", "usuario")
        .prefetch_related("quiz__questoes__alternativas"),
        id=tentativa_id,
        usuario=request.user,
        tipo_tentativa="QUIZ",
    )

    quiz = tentativa.quiz
    questoes = quiz.questoes.all()
    respostas_usuario = tentativa.respostas or {}

    revisao_questoes = []

    for indice, questao in enumerate(questoes, start=1):
        alternativas = list(questao.alternativas.all())
        alternativa_correta = next((a for a in alternativas if a.correta), None)
        alternativa_marcada_id = respostas_usuario.get(str(questao.id))

        acertou = False
        if alternativa_correta and alternativa_marcada_id:
            acertou = str(alternativa_correta.id) == str(alternativa_marcada_id)

        revisao_questoes.append({
            "numero": indice,
            "questao": questao,
            "alternativas": alternativas,
            "alternativa_correta_id": str(alternativa_correta.id) if alternativa_correta else None,
            "alternativa_marcada_id": str(alternativa_marcada_id) if alternativa_marcada_id else None,
            "acertou": acertou,
            "explicacao": questao.explicacao_resposta,
        })

    emoji_resultado = "📚"

    if tentativa.percentual_acertos == 100:
        emoji_resultado = "🏆"
    elif tentativa.percentual_acertos >= 70:
        emoji_resultado = "🎉"
    elif tentativa.percentual_acertos >= 40:
        emoji_resultado = "👏"
    else:
        emoji_resultado = "💪"

    contexto = {
        "tentativa": tentativa,
        "quiz": quiz,
        "mensagem_resultado": tentativa.desempenho_geral,
        "percentual_acertos": tentativa.percentual_acertos,
        "quantidade_acertos": tentativa.quantidade_acertos,
        "quantidade_erros": tentativa.quantidade_erros,
        "xp_ganho": tentativa.pontuacao,
        "revisao_questoes": revisao_questoes,
        "emoji_resultado": emoji_resultado,
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

    questoes = Questao.objects.select_related("disciplina").all()

    if request.method == "POST":
        form = QuizForm(request.POST)
        questoes_ids = request.POST.getlist("questoes")

        if form.is_valid():
            quiz = form.save()

            if questoes_ids:
                questoes_selecionadas = Questao.objects.filter(
                    id__in=questoes_ids,
                    disciplina=quiz.disciplina
                )
                quiz.questoes.set(questoes_selecionadas)

            messages.success(request, "Quiz criado com sucesso.")
            return redirect("quizzes:admin_lista_quizzes")
    else:
        form = QuizForm()

    contexto = {
        "form": form,
        "questoes": questoes,
        "questoes_marcadas": set(),
    }

    return render(request, "quizzes/admin/admin_form_quiz.html", contexto)


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

    if request.method == "POST":
        form = QuestaoForm(request.POST)

        letras = request.POST.getlist("letra[]")
        textos = request.POST.getlist("texto[]")
        correta = request.POST.get("correta")

        alternativas_validas = [texto for texto in textos if texto.strip()]

        if len(alternativas_validas) < 2:
            messages.error(request, "Cadastre pelo menos duas alternativas.")
        elif len(alternativas_validas) > 5:
            messages.error(request, "Cadastre no máximo cinco alternativas.")
        elif not correta:
            messages.error(request, "Marque uma alternativa correta.")
        elif form.is_valid():
            questao = form.save()

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
    else:
        form = QuestaoForm()

    contexto = {
        "form": form,
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

    alternativas = list(questao.alternativas.all().order_by("letra"))

    if request.method == "POST":
        form = QuestaoForm(request.POST, instance=questao)

        letras = request.POST.getlist("letra[]")
        textos = request.POST.getlist("texto[]")
        correta = request.POST.get("correta")

        alternativas_validas = [texto for texto in textos if texto.strip()]

        if len(alternativas_validas) < 2:
            messages.error(request, "Cadastre pelo menos duas alternativas.")
        elif len(alternativas_validas) > 5:
            messages.error(request, "Cadastre no máximo cinco alternativas.")
        elif not correta:
            messages.error(request, "Marque uma alternativa correta.")
        elif form.is_valid():
            questao = form.save()

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

    else:
        form = QuestaoForm(instance=questao)

    contexto = {
        "form": form,
        "questao": questao,
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


@login_required
def admin_editar_quiz(request, quiz_id):
    if not usuario_e_admin(request.user):
        return redirect("login")

    quiz = get_object_or_404(
        Quiz.objects.select_related("disciplina").prefetch_related("questoes"),
        id=quiz_id
    )

    questoes = Questao.objects.select_related("disciplina").all()
    questoes_marcadas = set(quiz.questoes.values_list("id", flat=True))

    if request.method == "POST":
        form = QuizForm(request.POST, instance=quiz)
        questoes_ids = request.POST.getlist("questoes")

        if form.is_valid():
            quiz = form.save()

            questoes_selecionadas = Questao.objects.filter(
                id__in=questoes_ids,
                disciplina=quiz.disciplina
            )
            quiz.questoes.set(questoes_selecionadas)

            messages.success(request, "Quiz atualizado com sucesso.")
            return redirect("quizzes:admin_lista_quizzes")
    else:
        form = QuizForm(instance=quiz)

    contexto = {
        "form": form,
        "quiz": quiz,
        "questoes": questoes,
        "questoes_marcadas": questoes_marcadas,
    }

    return render(request, "quizzes/admin/admin_form_quiz.html", contexto)


@login_required
def admin_excluir_quiz(request, quiz_id):
    if not usuario_e_admin(request.user):
        return redirect("login")

    quiz = get_object_or_404(
        Quiz.objects.select_related("disciplina").prefetch_related("questoes"),
        id=quiz_id
    )

    if request.method == "POST":
        quiz.delete()
        messages.success(request, "Quiz excluído com sucesso.")
        return redirect("quizzes:admin_lista_quizzes")

    contexto = {
        "quiz": quiz,
    }

    return render(request, "quizzes/admin/admin_confirmar_exclusao_quiz.html", contexto)
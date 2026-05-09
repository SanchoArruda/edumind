from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from quizzes.models import Tentativa, Questao
from usuarios.utils import usuario_e_admin, usuario_e_estudante

from .forms import DesafioForm
from .models import Desafio
from .utils import (
    calcular_estrelas_desafio,
    calcular_percentual_desafio,
    finalizar_tentativa_desafio,
    montar_revisao_desafio,
    obter_emoji_desafio,
    obter_mensagem_desafio,
)


@login_required
def inicio_desafios(request):
    if not usuario_e_estudante(request.user):
        return redirect("login")

    return render(request, "desafios/estudante/inicio_desafios.html")


@login_required
def lista_desafios(request):
    if not usuario_e_estudante(request.user):
        return redirect("login")

    tipo_prova = request.GET.get("tipo_prova")

    if tipo_prova not in ["ENADE", "POSCOMP"]:
        return redirect("desafios:inicio_desafios")

    desafios = Desafio.objects.filter(
        tipo_prova=tipo_prova,
        ativo=True
    ).prefetch_related(
        "questoes"
    ).order_by("ordem")

    tentativas_concluidas = Tentativa.objects.filter(
        usuario=request.user,
        tipo_tentativa="DESAFIO",
        concluida=True,
        aprovado=True,
        desafio__tipo_prova=tipo_prova,
    ).select_related("desafio")

    ordens_concluidas = set(
        tentativas_concluidas.values_list("desafio__ordem", flat=True)
    )

    desafios_liberados = []

    for desafio in desafios:
        concluido = desafio.ordem in ordens_concluidas

        if desafio.ordem == 1:
            liberado = True
        else:
            liberado = (desafio.ordem - 1) in ordens_concluidas

        desafios_liberados.append({
            "desafio": desafio,
            "liberado": liberado,
            "concluido": concluido,
        })

    contexto = {
        "tipo_prova": tipo_prova,
        "desafios_liberados": desafios_liberados,
    }

    return render(request, "desafios/estudante/lista_desafios.html", contexto)


@login_required
def iniciar_desafio(request, desafio_id):
    if not usuario_e_estudante(request.user):
        return redirect("login")

    desafio = get_object_or_404(
        Desafio.objects.prefetch_related("questoes"),
        id=desafio_id,
        ativo=True
    )

    if desafio.ordem > 1:
        desafio_anterior_concluido = Tentativa.objects.filter(
            usuario=request.user,
            tipo_tentativa="DESAFIO",
            desafio__tipo_prova=desafio.tipo_prova,
            desafio__ordem=desafio.ordem - 1,
            concluida=True,
            aprovado=True,
        ).exists()

        if not desafio_anterior_concluido:
            url = reverse("desafios:lista_desafios")
            return HttpResponseRedirect(f"{url}?tipo_prova={desafio.tipo_prova}")

    tentativa = Tentativa.objects.create(
        usuario=request.user,
        desafio=desafio,
        tipo_tentativa="DESAFIO",
        pontuacao=0,
        quantidade_acertos=0,
        quantidade_erros=0,
        percentual_acertos=0,
        desempenho_geral="",
        concluida=False,
        aprovado=False,
    )

    return redirect("desafios:responder_desafio", tentativa_id=tentativa.id)


@login_required
def responder_desafio(request, tentativa_id):
    if not usuario_e_estudante(request.user):
        return redirect("login")

    tentativa = get_object_or_404(
        Tentativa.objects.select_related(
            "desafio",
            "usuario"
        ).prefetch_related(
            "desafio__questoes__alternativas"
        ),
        id=tentativa_id,
        usuario=request.user,
        tipo_tentativa="DESAFIO",
    )

    if tentativa.concluida:
        return redirect("desafios:resultado_desafio", tentativa_id=tentativa.id)

    desafio = tentativa.desafio
    questoes = desafio.questoes.all()
    total_questoes = questoes.count()

    if request.method == "POST":
        finalizar_tentativa_desafio(
            tentativa=tentativa,
            questoes=questoes,
            post_data=request.POST,
        )

        return redirect("desafios:resultado_desafio", tentativa_id=tentativa.id)

    contexto = {
        "tentativa": tentativa,
        "desafio": desafio,
        "questoes": questoes,
        "total_questoes": total_questoes,
    }

    return render(request, "desafios/estudante/responder_desafio.html", contexto)


@login_required
def resultado_desafio(request, tentativa_id):
    if not usuario_e_estudante(request.user):
        return redirect("login")

    tentativa = get_object_or_404(
        Tentativa.objects.select_related(
            "desafio",
            "usuario"
        ).prefetch_related(
            "desafio__questoes__alternativas"
        ),
        id=tentativa_id,
        usuario=request.user,
        tipo_tentativa="DESAFIO",
    )

    desafio = tentativa.desafio
    questoes = desafio.questoes.all()
    respostas_usuario = tentativa.respostas or {}

    total_questoes = tentativa.quantidade_acertos + tentativa.quantidade_erros

    percentual_acertos = calcular_percentual_desafio(
        quantidade_acertos=tentativa.quantidade_acertos,
        total_questoes=total_questoes,
    )

    estrelas = calcular_estrelas_desafio(percentual_acertos)
    estrelas_preenchidas = range(estrelas)
    estrelas_vazias = range(5 - estrelas)

    mensagem_resultado = obter_mensagem_desafio(estrelas)

    revisao_questoes = montar_revisao_desafio(
        questoes=questoes,
        respostas_usuario=respostas_usuario,
    )

    emoji_resultado = obter_emoji_desafio(estrelas)

    proximo_desafio = Desafio.objects.filter(
        tipo_prova=desafio.tipo_prova,
        ordem=desafio.ordem + 1,
        ativo=True
    ).first()

    contexto = {
        "tentativa": tentativa,
        "desafio": desafio,
        "mensagem_resultado": mensagem_resultado,
        "percentual_acertos": percentual_acertos,
        "quantidade_acertos": tentativa.quantidade_acertos,
        "quantidade_erros": tentativa.quantidade_erros,
        "total_questoes": total_questoes,
        "estrelas": estrelas,
        "estrelas_preenchidas": estrelas_preenchidas,
        "estrelas_vazias": estrelas_vazias,
        "revisao_questoes": revisao_questoes,
        "emoji_resultado": emoji_resultado,
        "proximo_desafio": proximo_desafio,
    }

    return render(request, "desafios/estudante/resultado_desafio.html", contexto)


# ---------------------
# Admin
# ---------------------

@login_required
def admin_lista_desafios(request):
    if not usuario_e_admin(request.user):
        return redirect("login")

    filtro_tipo = request.GET.get("tipo", "").strip()

    desafios = Desafio.objects.all().order_by("tipo_prova", "ordem")

    if filtro_tipo in ["ENADE", "POSCOMP"]:
        desafios = desafios.filter(tipo_prova=filtro_tipo)

    contexto = {
        "desafios": desafios,
        "total_desafios": desafios.count(),
        "filtro_tipo": filtro_tipo,
    }

    return render(request, "desafios/admin/admin_lista_desafios.html", contexto)


@login_required
def admin_criar_desafio(request):
    if not usuario_e_admin(request.user):
        return redirect("login")

    questoes = Questao.objects.select_related(
        "disciplina"
    ).all().order_by(
        "disciplina__nome",
        "id"
    )

    if request.method == "POST":
        form = DesafioForm(request.POST)
        questoes_ids = request.POST.getlist("questoes")
        tempo_total_segundos = int(
            request.POST.get("tempo_total_segundos", 0) or 0
        )

        if form.is_valid():
            desafio = form.save(commit=False)
            desafio.tempo_total_segundos = tempo_total_segundos
            desafio.save()

            if questoes_ids:
                questoes_selecionadas = Questao.objects.filter(
                    id__in=questoes_ids
                )
                desafio.questoes.set(questoes_selecionadas)

            messages.success(request, "Desafio criado com sucesso.")
            return redirect("desafios:admin_lista_desafios")
    else:
        form = DesafioForm()

    contexto = {
        "form": form,
        "questoes": questoes,
        "questoes_marcadas": set(),
    }

    return render(request, "desafios/admin/admin_form_desafio.html", contexto)


@login_required
def admin_editar_desafio(request, desafio_id):
    if not usuario_e_admin(request.user):
        return redirect("login")

    desafio = get_object_or_404(
        Desafio.objects.prefetch_related("questoes"),
        id=desafio_id
    )

    questoes = Questao.objects.select_related(
        "disciplina"
    ).all().order_by(
        "disciplina__nome",
        "id"
    )

    questoes_marcadas = set(
        desafio.questoes.values_list("id", flat=True)
    )

    if request.method == "POST":
        form = DesafioForm(request.POST, instance=desafio)
        questoes_ids = request.POST.getlist("questoes")
        tempo_total_segundos = int(
            request.POST.get("tempo_total_segundos", 0) or 0
        )

        if form.is_valid():
            desafio = form.save(commit=False)
            desafio.tempo_total_segundos = tempo_total_segundos
            desafio.save()

            questoes_selecionadas = Questao.objects.filter(
                id__in=questoes_ids
            )
            desafio.questoes.set(questoes_selecionadas)

            messages.success(request, "Desafio atualizado com sucesso.")
            return redirect("desafios:admin_lista_desafios")
    else:
        form = DesafioForm(instance=desafio)

    contexto = {
        "form": form,
        "desafio": desafio,
        "questoes": questoes,
        "questoes_marcadas": questoes_marcadas,
    }

    return render(request, "desafios/admin/admin_form_desafio.html", contexto)


@login_required
def admin_excluir_desafio(request, desafio_id):
    if not usuario_e_admin(request.user):
        return redirect("login")

    desafio = get_object_or_404(Desafio, id=desafio_id)

    if request.method == "POST":
        desafio.delete()
        messages.success(request, "Desafio excluído com sucesso.")
        return redirect("desafios:admin_lista_desafios")

    contexto = {
        "desafio": desafio,
    }

    return render(
        request,
        "desafios/admin/admin_confirmar_exclusao_desafio.html",
        contexto
    )
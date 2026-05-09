from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404

from .forms import DisciplinaForm
from .models import Disciplina

from usuarios.utils import usuario_e_admin

@login_required
def admin_lista_disciplinas(request):
    if not usuario_e_admin(request.user):
        return redirect("login")

    disciplinas = Disciplina.objects.all().order_by("nome")

    contexto = {
        "disciplinas": disciplinas,
        "total_disciplinas": disciplinas.count(),
    }

    return render(request, "disciplinas/admin/admin_lista_disciplinas.html", contexto)


@login_required
def admin_criar_disciplina(request):
    if not usuario_e_admin(request.user):
        return redirect("login")

    if request.method == "POST":
        form = DisciplinaForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Disciplina cadastrada com sucesso.")
            return redirect("disciplinas:admin_lista_disciplinas")
    else:
        form = DisciplinaForm()

    contexto = {
        "form": form,
        "titulo_pagina": "Nova Disciplina",
        "botao_submit": "Cadastrar Disciplina",
    }

    return render(request, "disciplinas/admin/admin_form_disciplina.html", contexto)


@login_required
def admin_editar_disciplina(request, disciplina_id):
    if not usuario_e_admin(request.user):
        return redirect("login")

    disciplina = get_object_or_404(Disciplina, id=disciplina_id)

    if request.method == "POST":
        form = DisciplinaForm(request.POST, instance=disciplina)

        if form.is_valid():
            form.save()
            messages.success(request, "Disciplina atualizada com sucesso.")
            return redirect("disciplinas:admin_lista_disciplinas")
    else:
        form = DisciplinaForm(instance=disciplina)

    contexto = {
        "form": form,
        "disciplina": disciplina,
        "titulo_pagina": "Editar Disciplina",
        "botao_submit": "Salvar Alterações",
    }

    return render(request, "disciplinas/admin/admin_form_disciplina.html", contexto)


@login_required
def admin_excluir_disciplina(request, disciplina_id):
    if not usuario_e_admin(request.user):
        return redirect("login")

    disciplina = get_object_or_404(Disciplina, id=disciplina_id)

    if request.method == "POST":
        disciplina.delete()
        messages.success(request, "Disciplina excluída com sucesso.")
        return redirect("disciplinas:admin_lista_disciplinas")

    return redirect("disciplinas:admin_lista_disciplinas")
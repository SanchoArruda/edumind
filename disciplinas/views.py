from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404

from .models import Disciplina


def usuario_e_admin(user):
    return (
        user.is_authenticated
        and user.tipo_usuario
        and user.tipo_usuario.perfil.lower() == "administrador"
    )


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
        nome = request.POST.get("nome")

        if not nome:
            messages.error(request, "Informe o nome da disciplina.")
            return redirect("disciplinas:admin_criar_disciplina")

        if Disciplina.objects.filter(nome__iexact=nome).exists():
            messages.error(request, "Já existe uma disciplina com esse nome.")
            return redirect("disciplinas:admin_criar_disciplina")

        Disciplina.objects.create(nome=nome)

        messages.success(request, "Disciplina cadastrada com sucesso.")
        return redirect("disciplinas:admin_lista_disciplinas")

    return render(request, "disciplinas/admin/admin_form_disciplina.html")



@login_required
def admin_editar_disciplina(request, disciplina_id):
    if not usuario_e_admin(request.user):
        return redirect("login")

    disciplina = get_object_or_404(Disciplina, id=disciplina_id)

    if request.method == "POST":
        nome = request.POST.get("nome")

        if not nome:
            messages.error(request, "Informe o nome da disciplina.")
            return redirect("disciplinas:admin_editar_disciplina", disciplina_id=disciplina.id)

        if Disciplina.objects.filter(nome__iexact=nome).exclude(id=disciplina.id).exists():
            messages.error(request, "Já existe uma disciplina com esse nome.")
            return redirect("disciplinas:admin_editar_disciplina", disciplina_id=disciplina.id)

        disciplina.nome = nome
        disciplina.save()

        messages.success(request, "Disciplina atualizada com sucesso.")
        return redirect("disciplinas:admin_lista_disciplinas")

    contexto = {
        "disciplina": disciplina
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
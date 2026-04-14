from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect

from .forms import LoginForm, CadastroEstudanteForm
from .models import Usuario, Estudante


class UsuarioLoginView(LoginView):
    template_name = "usuarios/login.html"
    authentication_form = LoginForm

    def get_success_url(self):
        user = self.request.user

        if user.tipo_usuario == "administrador":
            return "/usuarios/admin-dashboard/"
        return "/usuarios/estudante-dashboard/"


def cadastro_estudante(request):
    if request.method == "POST":
        form = CadastroEstudanteForm(request.POST)

        if form.is_valid():
            nome = form.cleaned_data["nome"]
            email = form.cleaned_data["email"]
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            semestre = form.cleaned_data["semestre"]

            usuario = Usuario.objects.create_user(
                username=username,
                nome=nome,
                email=email,
                password=password,
                tipo_usuario="estudante"
            )

            Estudante.objects.create(
                usuario=usuario,
                semestre=semestre
            )

            messages.success(request, "Cadastro realizado com sucesso.")
            return redirect("login")
    else:
        form = CadastroEstudanteForm()

    return render(request, "usuarios/cadastro.html", {"form": form})


@login_required
def dashboard_estudante(request):
    if request.user.tipo_usuario != "estudante":
        return redirect("login")

    return render(request, "usuarios/dashboard_estudante.html")


@login_required
def dashboard_admin(request):
    if request.user.tipo_usuario != "administrador":
        return redirect("login")

    return render(request, "usuarios/dashboard_admin.html")


def sair(request):
    logout(request)
    return redirect("login")
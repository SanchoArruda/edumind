from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404

from django.db.models import Sum, Avg, Count, IntegerField, FloatField, Value
from django.db.models.functions import Coalesce

from .forms import LoginForm, CadastroEstudanteForm, UsuarioAdminForm
from .models import Usuario, TipoUsuario

from .utils import calcular_progresso_nivel


def usuario_e_admin(user):
    return (
        user.is_authenticated
        and user.tipo_usuario
        and user.tipo_usuario.perfil.lower() == "administrador"
    )

class UsuarioLoginView(LoginView):
    template_name = "usuarios/login.html"
    authentication_form = LoginForm

    def get_success_url(self):
        user = self.request.user

        if user.tipo_usuario and user.tipo_usuario.perfil.lower() == "administrador":
            return "/usuarios/admin-dashboard/"

        return "/usuarios/estudante-dashboard/"


def cadastro_estudante(request):
    if request.method == "POST":
        form = CadastroEstudanteForm(request.POST)

        if form.is_valid():
            tipo_estudante, _ = TipoUsuario.objects.get_or_create(
                perfil="Estudante"
            )

            Usuario.objects.create_user(
                username=form.cleaned_data["username"],
                nome=form.cleaned_data["nome"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
                tipo_usuario=tipo_estudante
            )

            messages.success(request, "Cadastro realizado com sucesso.")
            return redirect("login")
    else:
        form = CadastroEstudanteForm()

    return render(request, "usuarios/cadastro.html", {"form": form})


@login_required
def dashboard_estudante(request):
    if not request.user.tipo_usuario or request.user.tipo_usuario.perfil.lower() != "estudante":
        return redirect("login")

    from quizzes.models import Quiz, TentativaQuiz

    tentativas = TentativaQuiz.objects.filter(
        usuario=request.user,
        concluida=True
    ).select_related("quiz")

    quizzes_disponiveis = Quiz.objects.all().select_related("disciplina")[:3]

    total_quizzes_feitos = tentativas.count()
    total_acertos = sum(t.quantidade_acertos for t in tentativas)
    total_erros = sum(t.quantidade_erros for t in tentativas)
    total_questoes = total_acertos + total_erros
    xp_total = sum(t.pontuacao for t in tentativas)

    taxa_acerto = 0
    if total_questoes > 0:
        taxa_acerto = round((total_acertos / total_questoes) * 100, 1)

    progresso_nivel = calcular_progresso_nivel(xp_total)

    contexto = {
        "total_quizzes_feitos": total_quizzes_feitos,
        "total_acertos": total_acertos,
        "total_erros": total_erros,
        "total_questoes": total_questoes,
        "taxa_acerto": taxa_acerto,
        "xp_total": xp_total,
        "quizzes_disponiveis": quizzes_disponiveis,
        "tentativas_recentes": tentativas[:5],
        "nivel_atual": progresso_nivel["nivel_atual"],
        "xp_no_nivel": progresso_nivel["xp_no_nivel"],
        "xp_para_proximo_nivel": progresso_nivel["xp_para_proximo_nivel"],
        "xp_faltante": progresso_nivel["xp_faltante"],
        "percentual_nivel": progresso_nivel["percentual_nivel"],
    }

    return render(request, "usuarios/estudante/dashboard_estudante.html", contexto)


@login_required
def perfil_estudante(request):
    if not request.user.tipo_usuario or request.user.tipo_usuario.perfil.lower() != "estudante":
        return redirect("login")

    from quizzes.models import TentativaQuiz
    from .utils import calcular_progresso_nivel

    tentativas = TentativaQuiz.objects.filter(
        usuario=request.user,
        concluida=True
    ).select_related("quiz", "quiz__disciplina")

    total_quizzes = tentativas.count()
    total_acertos = sum(t.quantidade_acertos for t in tentativas)
    total_erros = sum(t.quantidade_erros for t in tentativas)
    total_questoes = total_acertos + total_erros
    xp_total = sum(t.pontuacao for t in tentativas)

    taxa_acerto = 0
    if total_questoes > 0:
        taxa_acerto = round((total_acertos / total_questoes) * 100, 1)

    progresso_nivel = calcular_progresso_nivel(xp_total)

    contexto = {
        "total_quizzes": total_quizzes,
        "total_acertos": total_acertos,
        "total_erros": total_erros,
        "total_questoes": total_questoes,
        "taxa_acerto": taxa_acerto,
        "xp_total": xp_total,
        "tentativas": tentativas[:10],

        "nivel_atual": progresso_nivel["nivel_atual"],
        "xp_no_nivel": progresso_nivel["xp_no_nivel"],
        "xp_para_proximo_nivel": progresso_nivel["xp_para_proximo_nivel"],
        "xp_faltante": progresso_nivel["xp_faltante"],
        "percentual_nivel": progresso_nivel["percentual_nivel"],
    }

    return render(request, "usuarios/estudante/perfil_estudante.html", contexto)


#-----------------------
#admin 
#-----------------------

@login_required
def dashboard_admin(request):
    if not request.user.tipo_usuario or request.user.tipo_usuario.perfil.lower() != "administrador":
        return redirect("login")

    return render(request, "usuarios/admin/dashboard_admin.html")


def sair(request):
    logout(request)
    return redirect("login")


@login_required
def admin_lista_estudantes(request):
    if not usuario_e_admin(request.user):
        return redirect("login")

    estudantes = Usuario.objects.select_related("tipo_usuario").filter(
        tipo_usuario__perfil__iexact="Estudante"
    ).order_by("nome")

    contexto = {
        "estudantes": estudantes,
        "total_estudantes": estudantes.count(),
    }

    return render(request, "usuarios/admin/admin_lista_estudantes.html", contexto)


@login_required
def admin_editar_estudante(request, usuario_id):
    if not usuario_e_admin(request.user):
        return redirect("login")

    estudante = get_object_or_404(
        Usuario.objects.select_related("tipo_usuario"),
        id=usuario_id,
        tipo_usuario__perfil__iexact="Estudante"
    )

    if request.method == "POST":
        form = UsuarioAdminForm(request.POST, instance=estudante)
        if form.is_valid():
            form.save()
            messages.success(request, "Estudante atualizado com sucesso.")
            return redirect("admin_lista_estudantes")
    else:
        form = UsuarioAdminForm(instance=estudante)

    contexto = {
        "form": form,
        "titulo": "Editar estudante",
        "botao": "Salvar alterações",
        "usuario_obj": estudante,
    }

    return render(request, "usuarios/admin/admin_form_estudante.html", contexto)


@login_required
def admin_excluir_estudante(request, usuario_id):
    if not usuario_e_admin(request.user):
        return redirect("login")

    estudante = get_object_or_404(
        Usuario.objects.select_related("tipo_usuario"),
        id=usuario_id,
        tipo_usuario__perfil__iexact="Estudante"
    )

    if request.method == "POST":
        estudante.delete()
        messages.success(request, "Estudante excluído com sucesso.")
        return redirect("admin_lista_estudantes")

    contexto = {
        "usuario_obj": estudante,
    }

    return render(
        request,
        "usuarios/admin/admin_confirmar_exclusao_estudante.html",
        contexto
    )


#admin- desempenho
@login_required
def admin_desempenho_geral(request):
    if not usuario_e_admin(request.user):
        return redirect("login")

    from quizzes.models import TentativaQuiz

    tentativas = TentativaQuiz.objects.filter(concluida=True).select_related(
        "usuario",
        "quiz",
        "quiz__disciplina",
    )

    total_tentativas = tentativas.count()
    total_estudantes_ativos = tentativas.values("usuario").distinct().count()

    totais = tentativas.aggregate(
        soma_acertos=Coalesce(
            Sum("quantidade_acertos"),
            Value(0),
            output_field=IntegerField()
        ),
        soma_erros=Coalesce(
            Sum("quantidade_erros"),
            Value(0),
            output_field=IntegerField()
        ),
        soma_pontos=Coalesce(
            Sum("pontuacao"),
            Value(0.0),
            output_field=FloatField()
        ),
    )

    total_acertos = totais["soma_acertos"]
    total_erros = totais["soma_erros"]
    pontuacao_total = round(totais["soma_pontos"], 1)

    total_questoes = total_acertos + total_erros

    taxa_media_acerto = 0
    if total_questoes > 0:
        taxa_media_acerto = round((total_acertos / total_questoes) * 100, 1)

    ranking_estudantes = (
        tentativas.values(
            "usuario__id",
            "usuario__nome",
            "usuario__username",
        )
        .annotate(
            total_tentativas=Count("id"),
            total_acertos=Coalesce(
                Sum("quantidade_acertos"),
                Value(0),
                output_field=IntegerField()
            ),
            total_erros=Coalesce(
                Sum("quantidade_erros"),
                Value(0),
                output_field=IntegerField()
            ),
            total_pontos=Coalesce(
                Sum("pontuacao"),
                Value(0.0),
                output_field=FloatField()
            ),
        )
        .order_by("-total_pontos", "-total_acertos")[:5]
    )

    quizzes_populares = (
        tentativas.values(
            "quiz__id",
            "quiz__titulo",
            "quiz__disciplina__nome",
        )
        .annotate(
            total_tentativas=Count("id"),
            media_pontos=Coalesce(
                Avg("pontuacao"),
                Value(0.0),
                output_field=FloatField()
            ),
            media_acertos=Coalesce(
                Avg("quantidade_acertos"),
                Value(0.0),
                output_field=FloatField()
            ),
        )
        .order_by("-total_tentativas", "-media_pontos")[:5]
    )

    contexto = {
        "total_tentativas": total_tentativas,
        "total_estudantes_ativos": total_estudantes_ativos,
        "taxa_media_acerto": taxa_media_acerto,
        "pontuacao_total": pontuacao_total,
        "ranking_estudantes": ranking_estudantes,
        "quizzes_populares": quizzes_populares,
    }

    return render(
        request,
        "usuarios/admin/admin_desempenho_geral.html",
        contexto,
    )

#--------------------------
#RANKING ESTUDANTE
#--------------------------


@login_required
def ranking_estudante(request):
    if not request.user.tipo_usuario or request.user.tipo_usuario.perfil.lower() != "estudante":
        return redirect("login")

    from quizzes.models import TentativaQuiz
    from django.db.models import Sum, Count, IntegerField, FloatField, Value
    from django.db.models.functions import Coalesce

    ranking_qs = (
        TentativaQuiz.objects.filter(concluida=True)
        .values(
            "usuario__id",
            "usuario__nome",
            "usuario__username",
        )
        .annotate(
            total_pontos=Coalesce(
                Sum("pontuacao"),
                Value(0.0),
                output_field=FloatField()
            ),
            total_acertos=Coalesce(
                Sum("quantidade_acertos"),
                Value(0),
                output_field=IntegerField()
            ),
            total_erros=Coalesce(
                Sum("quantidade_erros"),
                Value(0),
                output_field=IntegerField()
            ),
            total_tentativas=Count("id"),
        )
        .order_by("-total_pontos", "-total_acertos", "total_tentativas")
    )

    ranking = list(ranking_qs)
    minha_posicao = None

    for posicao, item in enumerate(ranking, start=1):
        total_questoes = item["total_acertos"] + item["total_erros"]

        taxa_acerto = 0
        if total_questoes > 0:
            taxa_acerto = round((item["total_acertos"] / total_questoes) * 100, 1)

        item["posicao"] = posicao
        item["taxa_acerto"] = taxa_acerto

        if item["usuario__id"] == request.user.id:
            minha_posicao = item

    contexto = {
        "ranking": ranking,
        "minha_posicao": minha_posicao,
    }

    return render(request, "usuarios/estudante/ranking_estudante.html", contexto)



#--------------------
# PERFIL - ESTUDANTE
#--------------------

@login_required
def meu_perfil(request):
    template_base = "base/base_dashboard.html"

    if request.user.tipo_usuario and request.user.tipo_usuario.perfil.lower() == "administrador":
        template_base = "base/base_admin.html"

    contexto = {
        "usuario_obj": request.user,
        "template_base": template_base,
    }

    return render(request, "usuarios/perfil.html", contexto)
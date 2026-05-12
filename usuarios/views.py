from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Sum, Avg, Count, IntegerField, FloatField, Value
from django.db.models.functions import Coalesce
from django.shortcuts import render, redirect, get_object_or_404

from desafios.models import Desafio
from disciplinas.models import Disciplina
from quizzes.models import Quiz, Questao, Tentativa

from .forms import LoginForm, CadastroEstudanteForm, UsuarioAdminForm
from .models import Usuario, TipoUsuario
from .utils import (
    usuario_e_admin,
    usuario_e_estudante,
    calcular_resumo_tentativas_quiz,
    montar_desempenho_por_area,
    adicionar_posicoes_ranking,
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
                tipo_usuario=tipo_estudante,
            )

            messages.success(request, "Cadastro realizado com sucesso.")
            return redirect("login")
    else:
        form = CadastroEstudanteForm()

    return render(request, "usuarios/cadastro.html", {"form": form})


@login_required
def dashboard_estudante(request):
    if not usuario_e_estudante(request.user):
        return redirect("login")

    tentativas = Tentativa.objects.filter(
        usuario=request.user,
        concluida=True,
        tipo_tentativa="QUIZ",
    ).select_related(
        "quiz",
        "quiz__disciplina",
    )

    tentativas_desafios = Tentativa.objects.filter(
        usuario=request.user,
        concluida=True,
        tipo_tentativa="DESAFIO",
    ).select_related("desafio")

    resumo_quizzes = calcular_resumo_tentativas_quiz(tentativas)
    progresso_nivel = resumo_quizzes["progresso_nivel"]

    desempenho_por_area_qs = (
        tentativas.values("quiz__disciplina__nome")
        .annotate(media_acerto=Avg("percentual_acertos"))
        .order_by("quiz__disciplina__nome")
    )

    desempenho_area = montar_desempenho_por_area(desempenho_por_area_qs)

    desafios_enade_concluidos = tentativas_desafios.filter(
        aprovado=True,
        desafio__tipo_prova="ENADE",
    ).count()

    desafios_poscomp_concluidos = tentativas_desafios.filter(
        aprovado=True,
        desafio__tipo_prova="POSCOMP",
    ).count()

    total_estrelas_desafios = tentativas_desafios.aggregate(
        total=Coalesce(
            Sum("pontuacao"),
            Value(0.0),
            output_field=FloatField()
        )
    )["total"]

    contexto = {
        # Quizzes
        "total_quizzes_feitos": resumo_quizzes["total_quizzes"],
        "total_acertos": resumo_quizzes["total_acertos"],
        "total_erros": resumo_quizzes["total_erros"],
        "total_questoes": resumo_quizzes["total_questoes"],
        "taxa_acerto": resumo_quizzes["taxa_acerto"],
        "xp_total": resumo_quizzes["xp_total"],

        # Nível
        "nivel_atual": progresso_nivel["nivel_atual"],
        "xp_no_nivel": progresso_nivel["xp_no_nivel"],
        "xp_para_proximo_nivel": progresso_nivel["xp_para_proximo_nivel"],
        "xp_faltante": progresso_nivel["xp_faltante"],
        "percentual_nivel": progresso_nivel["percentual_nivel"],

        # Desempenho por área — quizzes
        "labels_area": desempenho_area["labels_area"],
        "dados_area": desempenho_area["dados_area"],
        "desempenho_detalhado": desempenho_area["desempenho_detalhado"],
        "melhor_area": desempenho_area["melhor_area"],
        "pior_area": desempenho_area["pior_area"],

        # Desafios
        "desafios_enade_concluidos": desafios_enade_concluidos,
        "desafios_poscomp_concluidos": desafios_poscomp_concluidos,
        "total_estrelas_desafios": total_estrelas_desafios,
    }

    return render(request, "usuarios/estudante/dashboard_estudante.html", contexto)


@login_required
def perfil_estudante(request):
    if not usuario_e_estudante(request.user):
        return redirect("login")

    tentativas = Tentativa.objects.filter(
        usuario=request.user,
        concluida=True,
        tipo_tentativa="QUIZ",
    ).select_related(
        "quiz",
        "quiz__disciplina",
    )

    tentativas_desafios = Tentativa.objects.filter(
        usuario=request.user,
        concluida=True,
        tipo_tentativa="DESAFIO",
    ).select_related("desafio")

    resumo_quizzes = calcular_resumo_tentativas_quiz(tentativas)
    progresso_nivel = resumo_quizzes["progresso_nivel"]

    total_desafios_concluidos = tentativas_desafios.filter(
        aprovado=True
    ).count()

    melhor_estrelas_desafio = (
        tentativas_desafios.order_by("-pontuacao")
        .values_list("pontuacao", flat=True)
        .first()
        or 0
    )

    desafios_enade_concluidos = tentativas_desafios.filter(
        aprovado=True,
        desafio__tipo_prova="ENADE",
    ).count()

    desafios_poscomp_concluidos = tentativas_desafios.filter(
        aprovado=True,
        desafio__tipo_prova="POSCOMP",
    ).count()

    contexto = {
        "total_quizzes": resumo_quizzes["total_quizzes"],
        "total_acertos": resumo_quizzes["total_acertos"],
        "total_erros": resumo_quizzes["total_erros"],
        "total_questoes": resumo_quizzes["total_questoes"],
        "taxa_acerto": resumo_quizzes["taxa_acerto"],
        "xp_total": resumo_quizzes["xp_total"],
        "tentativas": tentativas[:10],

        "nivel_atual": progresso_nivel["nivel_atual"],
        "xp_no_nivel": progresso_nivel["xp_no_nivel"],
        "xp_para_proximo_nivel": progresso_nivel["xp_para_proximo_nivel"],
        "xp_faltante": progresso_nivel["xp_faltante"],
        "percentual_nivel": progresso_nivel["percentual_nivel"],

        # Desafios
        "tentativas_desafios": tentativas_desafios[:10],
        "total_desafios_concluidos": total_desafios_concluidos,
        "melhor_estrelas_desafio": melhor_estrelas_desafio,
        "desafios_enade_concluidos": desafios_enade_concluidos,
        "desafios_poscomp_concluidos": desafios_poscomp_concluidos,
    }

    return render(request, "usuarios/estudante/perfil_estudante.html", contexto)


# -----------------------
# ADMIN
# -----------------------


@login_required
def dashboard_admin(request):
    if not usuario_e_admin(request.user):
        return redirect("login")

    estudantes = Usuario.objects.filter(
        tipo_usuario__perfil__iexact="Estudante",
        is_active=True,
    )

    tentativas = Tentativa.objects.filter(
        concluida=True,
    ).select_related(
        "usuario",
        "quiz",
        "desafio",
    )

    contexto = {
        "total_estudantes": estudantes.count(),
        "total_quizzes": Quiz.objects.count(),
        "total_questoes": Questao.objects.count(),
        "total_desafios": Desafio.objects.count(),
        "total_disciplinas": Disciplina.objects.count(),
        "total_tentativas": tentativas.count(),
        "tentativas_recentes": tentativas.order_by("-id")[:5],
    }

    return render(request, "usuarios/admin/dashboard_admin.html", contexto)


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
        tipo_usuario__perfil__iexact="Estudante",
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
        tipo_usuario__perfil__iexact="Estudante",
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

#tirei temporariamente
# @login_required
# def admin_desempenho_geral(request):
#     if not usuario_e_admin(request.user):
#         return redirect("login")

#     tentativas = Tentativa.objects.filter(
#         concluida=True,
#         tipo_tentativa="QUIZ",
#     ).select_related(
#         "usuario",
#         "quiz",
#         "quiz__disciplina",
#     )

#     total_tentativas = tentativas.count()
#     total_estudantes_ativos = tentativas.values("usuario").distinct().count()

#     totais = tentativas.aggregate(
#         soma_acertos=Coalesce(
#             Sum("quantidade_acertos"),
#             Value(0),
#             output_field=IntegerField()
#         ),
#         soma_erros=Coalesce(
#             Sum("quantidade_erros"),
#             Value(0),
#             output_field=IntegerField()
#         ),
#         soma_pontos=Coalesce(
#             Sum("pontuacao"),
#             Value(0.0),
#             output_field=FloatField()
#         ),
#     )

#     total_acertos = totais["soma_acertos"]
#     total_erros = totais["soma_erros"]
#     pontuacao_total = round(totais["soma_pontos"], 1)

#     total_questoes = total_acertos + total_erros

#     taxa_media_acerto = 0
#     if total_questoes > 0:
#         taxa_media_acerto = round((total_acertos / total_questoes) * 100, 1)

#     ranking_estudantes = (
#         tentativas.values(
#             "usuario__id",
#             "usuario__nome",
#             "usuario__username",
#         )
#         .annotate(
#             total_tentativas=Count("id"),
#             total_acertos=Coalesce(
#                 Sum("quantidade_acertos"),
#                 Value(0),
#                 output_field=IntegerField()
#             ),
#             total_erros=Coalesce(
#                 Sum("quantidade_erros"),
#                 Value(0),
#                 output_field=IntegerField()
#             ),
#             total_pontos=Coalesce(
#                 Sum("pontuacao"),
#                 Value(0.0),
#                 output_field=FloatField()
#             ),
#         )
#         .order_by("-total_pontos", "-total_acertos")[:5]
#     )

#     quizzes_populares = (
#         tentativas.values(
#             "quiz__id",
#             "quiz__titulo",
#             "quiz__disciplina__nome",
#         )
#         .annotate(
#             total_tentativas=Count("id"),
#             media_pontos=Coalesce(
#                 Avg("pontuacao"),
#                 Value(0.0),
#                 output_field=FloatField()
#             ),
#             media_acertos=Coalesce(
#                 Avg("quantidade_acertos"),
#                 Value(0.0),
#                 output_field=FloatField()
#             ),
#         )
#         .order_by("-total_tentativas", "-media_pontos")[:5]
#     )

#     contexto = {
#         "total_tentativas": total_tentativas,
#         "total_estudantes_ativos": total_estudantes_ativos,
#         "taxa_media_acerto": taxa_media_acerto,
#         "pontuacao_total": pontuacao_total,
#         "ranking_estudantes": ranking_estudantes,
#         "quizzes_populares": quizzes_populares,
#     }

#     return render(
#         request,
#         "usuarios/admin/admin_desempenho_geral.html",
#         contexto,
#     )


# --------------------------
# RANKING ESTUDANTE
# --------------------------


@login_required
def ranking_estudante(request):
    if not usuario_e_estudante(request.user):
        return redirect("login")

    ranking_qs = (
        Tentativa.objects.filter(
            concluida=True,
            tipo_tentativa="QUIZ",
        )
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

    dados_ranking = adicionar_posicoes_ranking(
        ranking=ranking_qs,
        usuario_id=request.user.id,
    )

    contexto = {
        "ranking": dados_ranking["ranking"],
        "top_3": dados_ranking["top_3"],
        "ranking_restante": dados_ranking["ranking_restante"],
        "minha_posicao": dados_ranking["minha_posicao"],
    }

    return render(request, "usuarios/estudante/ranking_estudante.html", contexto)


# --------------------
# PERFIL - USUÁRIO
# --------------------

@login_required
def meu_perfil(request):
    template_base = "base/base_dashboard.html"

    if usuario_e_admin(request.user):
        template_base = "base/base_admin.html"

    contexto = {
        "usuario_obj": request.user,
        "template_base": template_base,
    }

    return render(request, "usuarios/perfil.html", contexto)



from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.http import HttpResponse
import traceback


@staff_member_required
def teste_email_online(request):
    try:
        resultado = send_mail(
            "Teste EduMind Online",
            "Este e-mail foi enviado diretamente pelo servidor online do Railway.",
            settings.DEFAULT_FROM_EMAIL,
            ["gucairesarruda@gmail.com"],
            fail_silently=False,
        )

        return HttpResponse(f"E-mail enviado com sucesso. Resultado: {resultado}")

    except Exception as erro:
        detalhes = traceback.format_exc()

        resposta = f"""
        <h2>Erro ao enviar e-mail</h2>
        <p><strong>Tipo:</strong> {type(erro).__name__}</p>
        <p><strong>Mensagem:</strong> {erro}</p>

        <hr>

        <h3>Configurações carregadas</h3>
        <p><strong>EMAIL_HOST:</strong> {settings.EMAIL_HOST}</p>
        <p><strong>EMAIL_PORT:</strong> {settings.EMAIL_PORT}</p>
        <p><strong>EMAIL_USE_TLS:</strong> {settings.EMAIL_USE_TLS}</p>
        <p><strong>EMAIL_HOST_USER:</strong> {settings.EMAIL_HOST_USER}</p>
        <p><strong>DEFAULT_FROM_EMAIL:</strong> {settings.DEFAULT_FROM_EMAIL}</p>
        <p><strong>Tamanho da senha SMTP:</strong> {len(settings.EMAIL_HOST_PASSWORD)}</p>

        <hr>

        <pre>{detalhes}</pre>
        """

        return HttpResponse(resposta, status=500)
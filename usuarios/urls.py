from django.urls import path
from django.contrib.auth import views as auth_views

from .views import (
    UsuarioLoginView,
    cadastro_estudante,
    dashboard_admin,
    dashboard_estudante,
    sair,
    admin_lista_estudantes,
    admin_editar_estudante,
    admin_excluir_estudante,
    ranking_estudante,
    meu_perfil,
    perfil_estudante,
)

urlpatterns = [
    path("login/", UsuarioLoginView.as_view(), name="login"),
    path("cadastro/", cadastro_estudante, name="cadastro"),
    path("logout/", sair, name="logout"),
    path("estudante-dashboard/", dashboard_estudante, name="dashboard_estudante"),
    path("admin-dashboard/", dashboard_admin, name="dashboard_admin"),

    # Recuperação de senha
    path("senha/esqueci/", auth_views.PasswordResetView.as_view(template_name="usuarios/senha_esqueci.html", email_template_name="usuarios/senha_email.html", subject_template_name="usuarios/senha_assunto.txt", success_url="/usuarios/senha/enviada/"), name="password_reset"),
    path("senha/enviada/", auth_views.PasswordResetDoneView.as_view(template_name="usuarios/senha_enviada.html"), name="password_reset_done"),
    path("senha/redefinir/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="usuarios/senha_redefinir.html", success_url="/usuarios/senha/concluida/"), name="password_reset_confirm"),
    path("senha/concluida/", auth_views.PasswordResetCompleteView.as_view(template_name="usuarios/senha_concluida.html"), name="password_reset_complete"),

    # Admin - estudantes
    path("admin/estudantes/", admin_lista_estudantes, name="admin_lista_estudantes"),
    path("admin/estudantes/<int:usuario_id>/editar/", admin_editar_estudante, name="admin_editar_estudante"),
    path("admin/estudantes/<int:usuario_id>/excluir/", admin_excluir_estudante, name="admin_excluir_estudante"),

    # Estudante - ranking
    path("ranking/", ranking_estudante, name="ranking_estudante"),

    # Estudante - perfil
    path("meu-perfil/", meu_perfil, name="meu_perfil"),
    path("perfil-estudante/", perfil_estudante, name="perfil_estudante"),

]
from django.urls import path
from . import views

app_name = "quizzes"

urlpatterns = [
    path("", views.lista_quizzes, name="lista_quizzes"),
    path("<int:quiz_id>/responder/", views.responder_quiz, name="responder_quiz"),
    path("resultado/<int:tentativa_id>/", views.resultado_quiz, name="resultado_quiz"),

    # área administrativa
    path("admin/quizzes/", views.admin_lista_quizzes, name="admin_lista_quizzes"),
    path("admin/quizzes/novo/", views.admin_criar_quiz, name="admin_criar_quiz"),

    path("admin/questoes/", views.admin_todas_questoes, name="admin_todas_questoes"),
    path("admin/questoes/nova/", views.admin_criar_questao_geral, name="admin_criar_questao_geral"),
    path("admin/questoes/<int:questao_id>/editar/", views.admin_editar_questao, name="admin_editar_questao"),
    path("admin/questoes/<int:questao_id>/excluir/", views.admin_excluir_questao, name="admin_excluir_questao"),

    path("admin/quizzes/<int:quiz_id>/questoes/", views.admin_lista_questoes, name="admin_lista_questoes"),
    path("admin/quizzes/<int:quiz_id>/questoes/nova/", views.admin_criar_questao, name="admin_criar_questao"),


]
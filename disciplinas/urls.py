from django.urls import path
from . import views

app_name = "disciplinas"

urlpatterns = [
    path("admin/disciplinas/", views.admin_lista_disciplinas, name="admin_lista_disciplinas"),
    path("admin/disciplinas/nova/", views.admin_criar_disciplina, name="admin_criar_disciplina"),

    
    path("admin/disciplinas/<int:disciplina_id>/editar/", views.admin_editar_disciplina, name="admin_editar_disciplina"),
    path("admin/disciplinas/<int:disciplina_id>/excluir/", views.admin_excluir_disciplina, name="admin_excluir_disciplina"),
]
from django.urls import path
from . import views

app_name = "desafios"

urlpatterns = [
    path("", views.inicio_desafios, name="inicio_desafios"),
    path("lista/", views.lista_desafios, name="lista_desafios"),
    path("<int:desafio_id>/iniciar/", views.iniciar_desafio, name="iniciar_desafio"),
    path("responder/<int:tentativa_id>/", views.responder_desafio, name="responder_desafio"),
    path("resultado/<int:tentativa_id>/", views.resultado_desafio, name="resultado_desafio"),

    path("admin/lista/", views.admin_lista_desafios, name="admin_lista_desafios"),
    path("admin/criar/", views.admin_criar_desafio, name="admin_criar_desafio"),
    path("admin/<int:desafio_id>/editar/", views.admin_editar_desafio, name="admin_editar_desafio"),
    path("admin/<int:desafio_id>/excluir/", views.admin_excluir_desafio, name="admin_excluir_desafio"),
]
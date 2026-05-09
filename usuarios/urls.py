from django.urls import path
from .views import (UsuarioLoginView, cadastro_estudante, dashboard_admin, dashboard_estudante, 
                    sair, admin_lista_estudantes, admin_editar_estudante, admin_excluir_estudante,
                    ranking_estudante,  meu_perfil, meu_perfil,perfil_estudante,)

urlpatterns = [
    path('login/', UsuarioLoginView.as_view(), name='login'),
    path('cadastro/', cadastro_estudante, name='cadastro'),
    path('logout/', sair, name='logout'),
    path('estudante-dashboard/', dashboard_estudante, name='dashboard_estudante'),
    path('admin-dashboard/', dashboard_admin, name='dashboard_admin'),

    #admin
    path('admin/estudantes/', admin_lista_estudantes, name='admin_lista_estudantes'),
    path("admin/estudantes/<int:usuario_id>/editar/", admin_editar_estudante, name="admin_editar_estudante"),
    path("admin/estudantes/<int:usuario_id>/excluir/", admin_excluir_estudante, name="admin_excluir_estudante"),

    #admin - desempenho
    #path("admin/desempenho-geral/", admin_desempenho_geral, name="admin_desempenho_geral"),

    #Estudante - ranking
    path("ranking/", ranking_estudante, name="ranking_estudante"),

    #Estudante - perfil
    path("meu-perfil/", meu_perfil, name="meu_perfil"),
    path("perfil-estudante/", perfil_estudante, name="perfil_estudante"),


]
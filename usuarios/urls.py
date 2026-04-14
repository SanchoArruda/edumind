from django.urls import path
from .views import UsuarioLoginView, cadastro_estudante, dashboard_admin, dashboard_estudante, sair

urlpatterns = [
    path('login/', UsuarioLoginView.as_view(), name='login'),
    path('cadastro/', cadastro_estudante, name='cadastro'),
    path('logout/', sair, name='logout'),
    path('estudante-dashboard/', dashboard_estudante, name='dashboard_estudante'),
    path('admin-dashboard/', dashboard_admin, name='dashboard_admin'),
]
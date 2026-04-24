from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),

    path('usuarios/', include('usuarios.urls')),
    path('quizzes/', include('quizzes.urls')),

    path('test/', TemplateView.as_view(template_name='base_dashboard.html'), name='home'),

     path('disciplinas/', include('disciplinas.urls')),
    
]

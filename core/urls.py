# Arquivo: core/urls.py
# Substitua COMPLETAMENTE o conteúdo do arquivo core/urls.py

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # URLs básicas
    path('', views.HomeView.as_view(), name='home'),
    path('mobile/', views.mobile_home, name='mobile_home'),
    path('status/', views.sistema_status, name='sistema_status'),
    
    # URLs sem CSRF
    path('login-simples/', views.login_sem_csrf, name='login_simples'),
    path('dashboard-simples/', views.dashboard_simples, name='dashboard_simples'),
]

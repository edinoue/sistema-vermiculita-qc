from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('mobile/', views.mobile_home, name='mobile_home'),
    path('status/', views.sistema_status, name='sistema_status'),
    path('login-simples/', views.login_sem_csrf, name='login_simples'),
    path('dashboard-simples/', views.dashboard_simples, name='dashboard_simples'),
]

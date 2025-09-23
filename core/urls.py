"""
URLs do app core
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Views principais
    path('', views.HomeView.as_view(), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]

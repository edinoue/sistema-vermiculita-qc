from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('mobile/', views.MobileHomeView.as_view(), name='mobile_home'),
    path('mobile-home/', views.mobile_home, name='mobile_home_alt'),
]

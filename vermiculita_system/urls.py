"""
URLs principais do sistema
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import HomeView, mobile_home, login_sem_csrf, dashboard_simples, sistema_status

urlpatterns = [
    # Página inicial
    path('', HomeView.as_view(), name='home'),
    
    # Admin do Django
    path('admin/', admin.site.urls),
    
    # URLs personalizadas sem CSRF
    path('login-simples/', login_sem_csrf, name='login_simples'),
    path('dashboard-simples/', dashboard_simples, name='dashboard_simples'),
    path('mobile/', mobile_home, name='mobile_home'),
    path('status/', sistema_status, name='sistema_status'),
    
    # URLs dos apps (mantidas para compatibilidade)
    path('core/', include('core.urls')),
    path('qc/', include('quality_control.urls')),
]

# Servir arquivos de media e static em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
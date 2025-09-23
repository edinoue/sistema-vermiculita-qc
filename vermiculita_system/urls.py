"""
URL Configuration for vermiculita_system project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('qc/', include('quality_control.urls')),
    path('', include('core.urls')),
]

# Servir arquivos de media em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Configurar títulos do admin
admin.site.site_header = "Sistema de Controle de Qualidade - Brasil Minérios"
admin.site.site_title = "Brasil Minérios QC"
admin.site.index_title = "Painel Administrativo"

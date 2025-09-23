# Arquivo: quality_control/urls.py
# Substitua COMPLETAMENTE o conteúdo do arquivo quality_control/urls.py

from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views

app_name = 'quality_control'

urlpatterns = [
    # Dashboard
    path('dashboard/', csrf_exempt(views.dashboard_view), name='dashboard'),
    
    # Análises pontuais
    path('spot-analysis/', csrf_exempt(views.SpotAnalysisListView.as_view()), name='spot_analysis_list'),
    path('spot-analysis/create/', csrf_exempt(views.SpotAnalysisCreateView.as_view()), name='spot_analysis_create'),
    
    # Laudos e relatórios
    path('reports/', csrf_exempt(views.reports_list_view), name='report_list'),
    
    # APIs
    path('api/product-properties/', csrf_exempt(views.get_product_properties), name='product_properties_api'),
    path('api/current-shift/', csrf_exempt(views.current_shift_api), name='current_shift_api'),
    path('api/dashboard-data/', csrf_exempt(views.dashboard_data_api), name='dashboard_data_api'),
]

"""
URLs do app quality_control
"""

from django.urls import path
from . import views

app_name = 'quality_control'

urlpatterns = [
    # Views principais
    path('', views.dashboard_view, name='dashboard'),
    path('dashboard/', views.dashboard_view, name='dashboard_main'),
    
    # Análises pontuais
    path('spot-analysis/', views.SpotAnalysisListView.as_view(), name='spot_analysis_list'),
    path('spot-analysis/create/', views.SpotAnalysisCreateView.as_view(), name='spot_analysis_create'),
    
    # Relatórios
    path('reports/', views.reports_list_view, name='reports_list'),
    
    # APIs
    path('api/product-properties/', views.get_product_properties, name='product_properties_api'),
    path('api/current-shift/', views.current_shift_api, name='current_shift_api'),
    path('api/dashboard-data/', views.dashboard_data_api, name='dashboard_data_api'),
]

"""
URLs do app quality_control
"""

from django.urls import path
from . import views, views_import, views_composite, views_spot_fixed, views_spot_improved, views_spot_grouped, views_reports, views_debug, views_production, views_spot_final, views_dashboard_new

app_name = 'quality_control'

urlpatterns = [
    # Views principais
    path('', views_dashboard_new.dashboard_new_view, name='dashboard'),
    path('dashboard/', views_dashboard_new.dashboard_new_view, name='dashboard_main'),
    path('dashboard/legacy/', views.dashboard_view, name='dashboard_legacy'),
    path('dashboard/spot/', views.spot_dashboard_view, name='spot_dashboard'),
    path('dashboard/spot/by-plant/', views.spot_dashboard_by_plant_view, name='spot_dashboard_by_plant'),
    path('debug/sequence/', views_debug.debug_sequence_view, name='debug_sequence'),
    
    # Seleção de tipo de análise
    path('analysis-type-selection/', views.analysis_type_selection_view, name='analysis_type_selection'),
    
    # Cadastro de Produção
    path('production-registration/', views_production.production_registration_list, name='production_registration_list'),
    path('production-registration/create/', views_production.production_registration_create, name='production_registration_create'),
    path('production-registration/<int:production_id>/', views_production.production_registration_detail, name='production_registration_detail'),
    path('production-registration/<int:production_id>/edit/', views_production.production_registration_edit, name='production_registration_edit'),
    path('api/active-production/', views_production.get_active_production, name='get_active_production'),
    
    # Sistema de Análise Pontual (Final)
    path('spot-analysis/', views_spot_final.spot_analysis_final_list, name='spot_analysis_list'),
    path('spot-analysis/create/', views_spot_final.spot_analysis_final_create, name='spot_analysis_create'),
    path('spot-analysis/<int:analysis_id>/', views_spot_final.spot_analysis_final_detail, name='spot_analysis_detail'),
    path('spot-analysis/<int:analysis_id>/edit/', views_spot_final.spot_analysis_final_edit, name='spot_analysis_edit'),
    
    # Sistema Legado (para compatibilidade)
    path('spot-analysis-legacy/', views.SpotAnalysisListView.as_view(), name='spot_analysis_legacy_list'),
    path('spot-analysis-legacy/create/', views.SpotAnalysisCreateView.as_view(), name='spot_analysis_legacy_create'),
    path('spot-analysis-legacy/create-fixed/', views_spot_fixed.spot_analysis_create_fixed, name='spot_analysis_create_fixed'),
    path('spot-analysis-legacy/create-improved/', views_spot_improved.spot_analysis_create_improved, name='spot_analysis_create_improved'),
    path('spot-analysis-legacy/<int:analysis_id>/edit/', views_spot_improved.spot_analysis_edit_improved, name='spot_analysis_edit_improved'),
    path('spot-analysis-legacy/<int:analysis_id>/detail/', views_spot_improved.spot_analysis_detail_improved, name='spot_analysis_detail_improved'),
    
    # Amostras Pontuais Agrupadas (Legado)
    path('spot-sample/', views_spot_grouped.spot_sample_list, name='spot_sample_list'),
    path('spot-sample/create/', views_spot_grouped.spot_sample_create, name='spot_sample_create'),
    path('spot-sample/<int:sample_id>/', views_spot_grouped.spot_sample_detail, name='spot_sample_detail'),
    path('spot-sample/<int:sample_id>/edit/', views_spot_grouped.spot_sample_edit, name='spot_sample_edit'),
    path('spot-sample/<int:sample_id>/delete/', views_spot_grouped.spot_sample_delete, name='spot_sample_delete'),
    
    # Amostras Compostas
    path('composite-sample/', views_composite.composite_sample_list, name='composite_sample_list'),
    path('composite-sample/create/', views_composite.composite_sample_create, name='composite_sample_create'),
    path('composite-sample/<int:sample_id>/', views_composite.composite_sample_detail, name='composite_sample_detail'),
    path('composite-sample/<int:sample_id>/edit/', views_composite.composite_sample_edit, name='composite_sample_edit'),
    
    # Relatórios
    path('reports/', views.reports_list_view, name='reports_list'),
    path('reports/generate/', views_reports.generate_report, name='generate_report'),
    path('reports/download/', views_reports.download_report, name='download_report'),
    
    # Importação de dados
    path('import/', views_import.import_dashboard, name='import_dashboard'),
    path('import/template/<int:template_id>/download/', views_import.download_template, name='download_template'),
    path('import/upload/', views_import.upload_data, name='upload_data'),
    path('import/status/<int:session_id>/', views_import.import_status, name='import_status'),
    path('import/errors/<int:session_id>/download/', views_import.download_errors, name='download_errors'),
    path('import/template/create/', views_import.create_template, name='create_template'),
    
    # APIs
    path('api/product-properties/', views.get_product_properties, name='product_properties_api'),
    path('api/current-shift/', views.current_shift_api, name='current_shift_api'),
    path('api/dashboard-data/', views.dashboard_data_api, name='dashboard_data_api'),
    path('dashboard-data/', views.dashboard_data_api, name='dashboard_data_api_alt'),
]

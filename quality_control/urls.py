# Arquivo: quality_control/urls.py
# Substitua o conteúdo do arquivo quality_control/urls.py

from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views, dashboard_views

app_name = 'quality_control'

# Aplicar csrf_exempt em todas as views
csrf_exempt_views = csrf_exempt(views.SpotAnalysisCreateView.as_view())
csrf_exempt_dashboard = csrf_exempt(dashboard_views.DashboardView.as_view())
csrf_exempt_control_chart = csrf_exempt(dashboard_views.ControlChartView.as_view())

urlpatterns = [
    # Dashboard
    path('dashboard/', csrf_exempt_dashboard, name='dashboard'),
    
    # Análises pontuais
    path('spot-analysis/create/', csrf_exempt_views, name='spot_analysis_create'),
    path('spot-analysis/', csrf_exempt(views.SpotAnalysisListView.as_view()), name='spot_analysis_list'),
    
    # Cartas de controle
    path('control-chart/', csrf_exempt_control_chart, name='control_chart'),
    path('control-chart/<str:product_code>/<str:property_name>/', 
         csrf_exempt(dashboard_views.ControlChartDetailView.as_view()), 
         name='control_chart_detail'),
    
    # Laudos e relatórios
    path('reports/', csrf_exempt(views.ReportListView.as_view()), name='report_list'),
    path('reports/create/', csrf_exempt(views.ReportCreateView.as_view()), name='report_create'),
    path('reports/<int:pk>/', csrf_exempt(views.ReportDetailView.as_view()), name='report_detail'),
    
    # APIs (sem CSRF)
    path('api/current-shift/', csrf_exempt(views.CurrentShiftAPIView.as_view()), name='current_shift_api'),
    path('api/shift-data/', csrf_exempt(views.ShiftDataAPIView.as_view()), name='shift_data_api'),
    path('api/dashboard-data/', csrf_exempt(dashboard_views.DashboardDataAPIView.as_view()), name='dashboard_data_api'),
]

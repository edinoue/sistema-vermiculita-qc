"""
URLs do app quality_control
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views, dashboard_views

app_name = 'quality_control'

# API Router
router = DefaultRouter()
router.register(r'products', api_views.ProductViewSet)
router.register(r'properties', api_views.PropertyViewSet)
router.register(r'spot-analyses', api_views.SpotAnalysisViewSet)
router.register(r'composite-samples', api_views.CompositeSampleViewSet)

urlpatterns = [
    # Web Views
    path('spot-analysis/', views.SpotAnalysisView.as_view(), name='spot_analysis'),
    path('spot-analysis/create/', views.SpotAnalysisCreateView.as_view(), name='spot_analysis_create'),
    path('composite-sample/', views.CompositeSampleView.as_view(), name='composite_sample'),
    path('composite-sample/create/', views.CompositeSampleCreateView.as_view(), name='composite_sample_create'),
    path('shift-summary/<str:date>/<str:shift>/<int:line_id>/', views.ShiftSummaryView.as_view(), name='shift_summary'),
    
    # Dashboard Views
    path('dashboard/', dashboard_views.DashboardView.as_view(), name='dashboard'),
    path('control-chart/', dashboard_views.ControlChartView.as_view(), name='control_chart'),
    path('capability-analysis/', dashboard_views.CapabilityAnalysisView.as_view(), name='capability_analysis'),
    path('correlation-analysis/', dashboard_views.CorrelationAnalysisView.as_view(), name='correlation_analysis'),
    
    # API URLs
    path('', include(router.urls)),
    path('current-shift/', api_views.CurrentShiftView.as_view(), name='current_shift'),
    path('shift-data/<str:date>/<str:shift>/<int:line_id>/', api_views.ShiftDataView.as_view(), name='shift_data'),
    
    # Dashboard API URLs
    path('api/dashboard-data/', dashboard_views.DashboardDataAPIView.as_view(), name='dashboard_data_api'),
    path('api/control-chart-data/', dashboard_views.ControlChartDataAPIView.as_view(), name='control_chart_data_api'),
    path('api/capability-data/', dashboard_views.CapabilityDataAPIView.as_view(), name='capability_data_api'),
]

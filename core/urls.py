"""
URLs do app core
"""

from django.urls import path
from . import views, auxiliary_views

app_name = 'core'

urlpatterns = [
    # Views principais
    path('', views.HomeView.as_view(), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('mobile/', views.MobileHomeView.as_view(), name='mobile_home'),
    
    # QR Codes e visualizações públicas
    path('qr/<str:line_code>/', auxiliary_views.QRCodeView.as_view(), name='qr_code'),
    path('line-summary/<str:line_code>/', auxiliary_views.LineSummaryView.as_view(), name='line_summary'),
    path('shift-summary/<str:date>/<str:shift>/<int:line_id>/', auxiliary_views.ShiftSummaryView.as_view(), name='shift_summary'),
    path('generate-shift-qr/<int:line_id>/<str:date_str>/<str:shift_name>/', auxiliary_views.generate_shift_qr, name='generate_shift_qr'),
    
    # Exportação e importação de dados
    path('export/', auxiliary_views.DataExportView.as_view(), name='data_export'),
    path('export/data/', auxiliary_views.export_data, name='export_data'),
    path('import/', auxiliary_views.DataImportView.as_view(), name='data_import'),
    
    # Backup e restore
    path('backup/', auxiliary_views.BackupView.as_view(), name='backup'),
    path('backup/create/', auxiliary_views.create_backup, name='create_backup'),
    
    # APIs
    path('api/system-stats/', auxiliary_views.SystemStatsAPIView.as_view(), name='system_stats_api'),
]

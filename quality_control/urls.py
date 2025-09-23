# Arquivo: quality_control/urls.py
# Substitua COMPLETAMENTE o conteúdo do arquivo quality_control/urls.py

from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from . import views

app_name = 'quality_control'

# View simples para páginas que ainda não existem
def pagina_em_desenvolvimento(request):
    html = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Em Desenvolvimento - Brasil Minérios</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header text-center bg-warning">
                            <h4><i class="bi bi-tools"></i> Em Desenvolvimento</h4>
                        </div>
                        <div class="card-body text-center">
                            <p class="lead">Esta funcionalidade está sendo desenvolvida.</p>
                            <p>Por enquanto, use o <strong>Admin do Django</strong> para gerenciar os dados.</p>
                            <div class="d-grid gap-2">
                                <a href="/admin/" class="btn btn-primary">
                                    <i class="bi bi-gear"></i> Ir para Admin
                                </a>
                                <a href="/" class="btn btn-outline-secondary">
                                    <i class="bi bi-house"></i> Voltar ao Início
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)

urlpatterns = [
    # Dashboard - página em desenvolvimento
    path('dashboard/', csrf_exempt(pagina_em_desenvolvimento), name='dashboard'),
    
    # Análises pontuais - página em desenvolvimento
    path('spot-analysis/create/', csrf_exempt(pagina_em_desenvolvimento), name='spot_analysis_create'),
    path('spot-analysis/', csrf_exempt(pagina_em_desenvolvimento), name='spot_analysis_list'),
    
    # Cartas de controle - página em desenvolvimento
    path('control-chart/', csrf_exempt(pagina_em_desenvolvimento), name='control_chart'),
    
    # Laudos e relatórios - página em desenvolvimento
    path('reports/', csrf_exempt(pagina_em_desenvolvimento), name='report_list'),
    path('reports/create/', csrf_exempt(pagina_em_desenvolvimento), name='report_create'),
    
    # APIs básicas (se existirem)
    path('api/current-shift/', csrf_exempt(pagina_em_desenvolvimento), name='current_shift_api'),
    path('api/shift-data/', csrf_exempt(pagina_em_desenvolvimento), name='shift_data_api'),
]

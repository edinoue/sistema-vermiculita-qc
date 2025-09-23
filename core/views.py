# Arquivo: core/views.py
# Substitua o conteúdo do arquivo core/views.py por este código

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib import messages
import json

@method_decorator(csrf_exempt, name='dispatch')
class HomeView(TemplateView):
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sistema_online'] = True
        context['empresa'] = 'Brasil Minérios'
        return context

@csrf_exempt
def mobile_home(request):
    """View para interface mobile"""
    return render(request, 'core/mobile_home.html', {
        'sistema_online': True,
        'empresa': 'Brasil Minérios',
        'versao': '1.0.0'
    })

@csrf_exempt
def login_sem_csrf(request):
    """Login personalizado sem CSRF"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', '/dashboard-simples/')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuário ou senha incorretos')
    
    html = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login - Brasil Minérios</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
        <style>
            body {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .card {
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
        </style>
    </head>
    <body class="d-flex align-items-center">
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-md-6 col-lg-4">
                    <div class="card">
                        <div class="card-header text-center bg-primary text-white">
                            <h4><i class="bi bi-shield-lock"></i> Acesso ao Sistema</h4>
                            <p class="mb-0">Brasil Minérios</p>
                        </div>
                        <div class="card-body p-4">
                            <form method="post">
                                <div class="mb-3">
                                    <label for="username" class="form-label">
                                        <i class="bi bi-person"></i> Usuário:
                                    </label>
                                    <input type="text" class="form-control form-control-lg" 
                                           id="username" name="username" required 
                                           placeholder="Digite seu usuário">
                                </div>
                                <div class="mb-4">
                                    <label for="password" class="form-label">
                                        <i class="bi bi-lock"></i> Senha:
                                    </label>
                                    <input type="password" class="form-control form-control-lg" 
                                           id="password" name="password" required 
                                           placeholder="Digite sua senha">
                                </div>
                                <div class="d-grid">
                                    <button type="submit" class="btn btn-primary btn-lg">
                                        <i class="bi bi-box-arrow-in-right"></i> Entrar
                                    </button>
                                </div>
                            </form>
                        </div>
                        <div class="card-footer text-center text-muted">
                            <small>Sistema de Controle de Qualidade v1.0</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)

@csrf_exempt
def dashboard_simples(request):
    """Dashboard simples sem CSRF"""
    if not request.user.is_authenticated:
        return redirect('/login-simples/?next=/dashboard-simples/')
    
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard - Brasil Minérios</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/">
                    <i class="bi bi-gem"></i> Brasil Minérios
                </a>
                <div class="navbar-nav ms-auto">
                    <span class="navbar-text me-3">
                        <i class="bi bi-person-circle"></i> {request.user.username}
                    </span>
                    <a class="nav-link" href="/admin/">
                        <i class="bi bi-gear"></i> Admin
                    </a>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <div class="row">
                <div class="col-12">
                    <div class="alert alert-success">
                        <h4><i class="bi bi-check-circle"></i> Bem-vindo ao Sistema!</h4>
                        <p class="mb-0">Login realizado com sucesso. Todas as funcionalidades estão disponíveis.</p>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-3 mb-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <i class="bi bi-clipboard-data text-primary fs-1"></i>
                            <h5 class="card-title">Análises</h5>
                            <p class="card-text">Registro de qualidade</p>
                            <a href="/admin/" class="btn btn-primary">Acessar</a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-3 mb-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <i class="bi bi-graph-up text-success fs-1"></i>
                            <h5 class="card-title">Dashboard</h5>
                            <p class="card-text">Gráficos e SPC</p>
                            <a href="/admin/" class="btn btn-success">Acessar</a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-3 mb-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <i class="bi bi-file-pdf text-info fs-1"></i>
                            <h5 class="card-title">Laudos</h5>
                            <p class="card-text">Relatórios PDF</p>
                            <a href="/admin/" class="btn btn-info">Acessar</a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-3 mb-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <i class="bi bi-gear text-secondary fs-1"></i>
                            <h5 class="card-title">Admin</h5>
                            <p class="card-text">Configurações</p>
                            <a href="/admin/" class="btn btn-secondary">Acessar</a>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="bi bi-info-circle"></i> Informações do Sistema</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <p><strong>Empresa:</strong> Brasil Minérios</p>
                                    <p><strong>Versão:</strong> 1.0.0</p>
                                    <p><strong>Status:</strong> <span class="badge bg-success">Operacional</span></p>
                                </div>
                                <div class="col-md-6">
                                    <p><strong>Usuário:</strong> {request.user.username}</p>
                                    <p><strong>Plataforma:</strong> Railway</p>
                                    <p><strong>Banco:</strong> PostgreSQL</p>
                                </div>
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

@csrf_exempt
def sistema_status(request):
    """API para verificar status do sistema"""
    return JsonResponse({
        'status': 'operacional',
        'empresa': 'Brasil Minérios',
        'versao': '1.0.0',
        'csrf_disabled': True,
        'usuario_logado': request.user.is_authenticated,
        'usuario': request.user.username if request.user.is_authenticated else None,
        'plataforma': 'Railway',
        'banco': 'PostgreSQL'
    })

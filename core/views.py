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
        return context

@csrf_exempt
def mobile_home(request):
    """View para interface mobile"""
    return render(request, 'core/mobile_home.html', {
        'sistema_online': True,
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
            return redirect('/admin/')
        else:
            messages.error(request, 'Usuário ou senha incorretos')
    
    html = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login - Sistema Vermiculita</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container">
            <div class="row justify-content-center mt-5">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h4 class="text-center">🔐 Login - Sistema Vermiculita</h4>
                        </div>
                        <div class="card-body">
                            <form method="post">
                                <div class="mb-3">
                                    <label for="username" class="form-label">Usuário:</label>
                                    <input type="text" class="form-control" id="username" name="username" value="admin" required>
                                </div>
                                <div class="mb-3">
                                    <label for="password" class="form-label">Senha:</label>
                                    <input type="password" class="form-control" id="password" name="password" value="admin123" required>
                                </div>
                                <div class="d-grid">
                                    <button type="submit" class="btn btn-primary">Entrar</button>
                                </div>
                            </form>
                            <div class="mt-3 text-center">
                                <small class="text-muted">
                                    Usuário padrão: <strong>admin</strong><br>
                                    Senha padrão: <strong>admin123</strong>
                                </small>
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
def dashboard_simples(request):
    """Dashboard simples sem CSRF"""
    if not request.user.is_authenticated:
        return redirect('/login-simples/')
    
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard - Sistema Vermiculita</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="#">Sistema Vermiculita</a>
                <div class="navbar-nav ms-auto">
                    <span class="navbar-text">Olá, {request.user.username}!</span>
                    <a class="nav-link" href="/admin/">Admin</a>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <div class="row">
                <div class="col-12">
                    <div class="alert alert-success">
                        <h4>🎉 Sistema Funcionando!</h4>
                        <p>Login realizado com sucesso. O sistema está operacional.</p>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-body text-center">
                            <h5>📊 Dashboard</h5>
                            <p>Gráficos e estatísticas</p>
                            <a href="/admin/" class="btn btn-primary">Acessar</a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-body text-center">
                            <h5>📝 Análises</h5>
                            <p>Registro de qualidade</p>
                            <a href="/admin/" class="btn btn-success">Acessar</a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-body text-center">
                            <h5>📄 Laudos</h5>
                            <p>Relatórios e ordens</p>
                            <a href="/admin/" class="btn btn-info">Acessar</a>
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
        'status': 'online',
        'versao': '1.0.0',
        'csrf_disabled': True,
        'usuario_logado': request.user.is_authenticated,
        'usuario': request.user.username if request.user.is_authenticated else None
    })

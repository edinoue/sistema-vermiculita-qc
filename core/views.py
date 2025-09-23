from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from django.views import View

class HomeView(TemplateView):
    """
    View da página inicial
    """
    template_name = 'core/home.html'

class LoginView(View):
    """
    View de login
    """
    template_name = 'registration/login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('quality_control:dashboard')
        return render(request, self.template_name)
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'quality_control:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
            return render(request, self.template_name)

def logout_view(request):
    """
    View de logout
    """
    logout(request)
    messages.success(request, 'Logout realizado com sucesso.')
    return redirect('core:home')

"""
Views do app core
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, time

from .models import ProductionLine, Shift
from quality_control.models import SpotAnalysis, CompositeSample


class HomeView(TemplateView):
    """
    Página inicial - redireciona baseado no dispositivo
    """
    template_name = 'core/home.html'
    
    def get(self, request, *args, **kwargs):
        # Detectar se é mobile e redirecionar
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        is_mobile = any(device in user_agent for device in ['mobile', 'android', 'iphone'])
        
        if is_mobile:
            return redirect('core:mobile_home')
        
        if request.user.is_authenticated:
            return redirect('quality_control:dashboard')
        
        return super().get(request, *args, **kwargs)


class LoginView(View):
    """
    View de login
    """
    template_name = 'core/login.html'
    
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


class LogoutView(View):
    """
    View de logout
    """
    def get(self, request):
        logout(request)
        return redirect('core:home')


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Dashboard principal do sistema
    """
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estatísticas básicas
        today = timezone.now().date()
        context.update({
            'today': today,
            'total_lines': ProductionLine.objects.filter(is_active=True).count(),
            'today_spot_analyses': SpotAnalysis.objects.filter(date=today).count(),
            'today_composite_samples': CompositeSample.objects.filter(date=today).count(),
        })
        
        return context


class MobileHomeView(TemplateView):
    """
    Página inicial otimizada para mobile
    """
    template_name = 'core/mobile_home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Informações do turno atual
        current_time = timezone.now().time()
        current_shift = self.get_current_shift(current_time)
        
        context.update({
            'current_shift': current_shift,
            'production_lines': ProductionLine.objects.filter(is_active=True),
            'current_time': timezone.now(),
        })
        
        return context
    
    def get_current_shift(self, current_time):
        """
        Determina o turno atual baseado no horário
        """
        try:
            # Turno A: 06:00 - 18:00
            if time(6, 0) <= current_time < time(18, 0):
                return Shift.objects.get(name='A')
            # Turno B: 18:00 - 06:00
            else:
                return Shift.objects.get(name='B')
        except Shift.DoesNotExist:
            return None


class QRCodeView(TemplateView):
    """
    View acessada via QR Code para mostrar dados do turno atual
    """
    template_name = 'core/qr_shift_summary.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        line_code = kwargs.get('line_code')
        production_line = get_object_or_404(ProductionLine, code=line_code, is_active=True)
        
        # Determinar turno atual
        current_time = timezone.now().time()
        today = timezone.now().date()
        
        if time(6, 0) <= current_time < time(18, 0):
            current_shift = Shift.objects.get(name='A')
        else:
            current_shift = Shift.objects.get(name='B')
        
        # Buscar análises pontuais do turno atual
        spot_analyses = SpotAnalysis.objects.filter(
            production_line=production_line,
            date=today,
            shift=current_shift
        ).order_by('-sample_time')
        
        # Buscar amostra composta do turno atual
        try:
            composite_sample = CompositeSample.objects.get(
                production_line=production_line,
                date=today,
                shift=current_shift
            )
        except CompositeSample.DoesNotExist:
            composite_sample = None
        
        context.update({
            'production_line': production_line,
            'current_shift': current_shift,
            'today': today,
            'spot_analyses': spot_analyses,
            'composite_sample': composite_sample,
        })
        
        return context

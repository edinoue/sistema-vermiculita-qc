"""
Views simplificadas para evitar problemas de CSRF
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json

from core.models import Plant, ProductionLine, Shift
from .models import Product, Property, Specification, SpotAnalysis, CompositeSample, ChemicalAnalysis, AnalysisType, AnalysisTypeProperty

@login_required
def dashboard_view(request):
    """Dashboard principal do sistema de controle de qualidade"""
    today = timezone.now().date()
    
    # Estatísticas gerais
    total_products = Product.objects.filter(is_active=True).count()
    total_lines = ProductionLine.objects.filter(is_active=True).count()
    total_analyses = SpotAnalysis.objects.count()
    
    # Análises de hoje
    today_analyses = SpotAnalysis.objects.filter(sample_time__date=today)
    today_count = today_analyses.count()
    
    # Análises recentes
    recent_analyses = SpotAnalysis.objects.select_related(
        'product', 'production_line', 'property'
    ).order_by('-sample_time')[:10]
    
    # Produtos mais analisados hoje
    top_products_today = today_analyses.values(
        'product__name', 'product__code'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    context = {
        'today': today,
        'total_products': total_products,
        'total_lines': total_lines,
        'total_analyses': total_analyses,
        'today_count': today_count,
        'recent_analyses': recent_analyses,
        'top_products_today': top_products_today,
    }
    
    return render(request, 'quality_control/dashboard.html', context)

@method_decorator(login_required, name='dispatch')
class SpotAnalysisListView(ListView):
    model = SpotAnalysis
    template_name = 'quality_control/spot_analysis_list.html'
    context_object_name = 'analyses'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = SpotAnalysis.objects.select_related(
            'product', 'production_line', 'property', 'analysis_type'
        ).order_by('-sample_time')
        
        # Filtros opcionais
        product_id = self.request.GET.get('product')
        line_id = self.request.GET.get('line')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if line_id:
            queryset = queryset.filter(production_line_id=line_id)
        if date_from:
            queryset = queryset.filter(sample_time__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(sample_time__date__lte=date_to)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.filter(is_active=True)
        context['lines'] = ProductionLine.objects.filter(is_active=True)
        context['total_analyses'] = self.get_queryset().count()
        return context

@login_required
def analysis_type_selection_view(request):
    """Seleção do tipo de análise"""
    analysis_types = AnalysisType.objects.filter(is_active=True)
    
    context = {
        'analysis_types': analysis_types,
    }
    
    return render(request, 'quality_control/analysis_type_selection.html', context)

@login_required
def spot_analysis_create_simple(request):
    """Criação simplificada de análise pontual"""
    if request.method == 'POST':
        try:
            # Obter dados do formulário
            analysis_type_id = request.POST.get('analysis_type')
            date = request.POST.get('date')
            product_id = request.POST.get('product')
            production_line_id = request.POST.get('production_line')
            shift_id = request.POST.get('shift')
            sample_time = request.POST.get('sample_time')
            sequence = request.POST.get('sequence')
            
            # Criar análise
            analysis = SpotAnalysis.objects.create(
                analysis_type_id=analysis_type_id,
                date=date,
                product_id=product_id,
                production_line_id=production_line_id,
                shift_id=shift_id,
                sample_time=sample_time,
                sequence=sequence,
                property_id=1,  # Propriedade padrão
                value=0,
                unit='%',
                test_method='Método padrão',
                status='PENDENTE'
            )
            
            messages.success(request, 'Análise criada com sucesso!')
            return redirect('quality_control:spot_analysis_list')
            
        except Exception as e:
            messages.error(request, f'Erro ao criar análise: {str(e)}')
    
    # Obter dados para o formulário
    analysis_types = AnalysisType.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)
    lines = ProductionLine.objects.filter(is_active=True)
    shifts = Shift.objects.all()
    
    context = {
        'analysis_types': analysis_types,
        'products': products,
        'lines': lines,
        'shifts': shifts,
    }
    
    return render(request, 'quality_control/spot_analysis_create_simple.html', context)

@login_required
def reports_list_view(request):
    """Lista de laudos e relatórios"""
    from datetime import datetime, timedelta
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=365)
    
    analyses_by_month = []
    current_date = start_date
    while current_date <= end_date:
        month_start = current_date.replace(day=1)
        if current_date.month == 12:
            month_end = current_date.replace(year=current_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = current_date.replace(month=current_date.month + 1, day=1) - timedelta(days=1)
        
        count = SpotAnalysis.objects.filter(
            sample_time__date__range=[month_start, month_end]
        ).count()
        
        if count > 0:
            analyses_by_month.append({
                'month': month_start.strftime('%Y-%m'),
                'count': count
            })
        
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1, day=1)
    
    top_products = SpotAnalysis.objects.values(
        'product__name', 'product__code'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    context = {
        'analyses_by_month': analyses_by_month,
        'top_products': list(top_products),
        'total_analyses': SpotAnalysis.objects.count(),
    }
    return render(request, 'quality_control/reports_list.html', context)







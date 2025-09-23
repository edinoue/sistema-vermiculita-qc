# Arquivo: quality_control/views.py
# Substitua COMPLETAMENTE o conteúdo do arquivo quality_control/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, CreateView, DetailView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json

from core.models import Plant, ProductionLine, Shift
from .models import Product, Property, Specification, SpotAnalysis, CompositeAnalysis, ChemicalAnalysis

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class SpotAnalysisListView(ListView):
    model = SpotAnalysis
    template_name = 'quality_control/spot_analysis_list.html'
    context_object_name = 'analyses'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = SpotAnalysis.objects.select_related(
            'product', 'line', 'shift', 'operator'
        ).order_by('-analysis_datetime')
        
        # Filtros
        product_id = self.request.GET.get('product')
        line_id = self.request.GET.get('line')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if line_id:
            queryset = queryset.filter(line_id=line_id)
        if date_from:
            queryset = queryset.filter(analysis_datetime__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(analysis_datetime__date__lte=date_to)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        context['lines'] = ProductionLine.objects.all()
        context['total_analyses'] = self.get_queryset().count()
        return context

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class SpotAnalysisCreateView(CreateView):
    model = SpotAnalysis
    template_name = 'quality_control/spot_analysis_create.html'
    fields = ['product', 'line', 'shift', 'analysis_datetime', 'sample_id', 'observations']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        context['lines'] = ProductionLine.objects.all()
        context['shifts'] = Shift.objects.all()
        
        # Turno atual
        current_hour = timezone.now().hour
        if 6 <= current_hour < 18:
            current_shift = Shift.objects.filter(name='A').first()
        else:
            current_shift = Shift.objects.filter(name='B').first()
        context['current_shift'] = current_shift
        
        return context
    
    def form_valid(self, form):
        form.instance.operator = self.request.user
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Análise pontual criada com sucesso!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return '/qc/spot-analysis/'

@csrf_exempt
@login_required
def dashboard_view(request):
    """Dashboard principal com estatísticas"""
    
    # Estatísticas gerais
    total_analyses = SpotAnalysis.objects.count()
    today_analyses = SpotAnalysis.objects.filter(
        analysis_datetime__date=timezone.now().date()
    ).count()
    
    # Análises por produto (últimos 30 dias)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    analyses_by_product = SpotAnalysis.objects.filter(
        analysis_datetime__gte=thirty_days_ago
    ).values('product__name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Análises por linha (últimos 7 dias)
    seven_days_ago = timezone.now() - timedelta(days=7)
    analyses_by_line = SpotAnalysis.objects.filter(
        analysis_datetime__gte=seven_days_ago
    ).values('line__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Análises recentes
    recent_analyses = SpotAnalysis.objects.select_related(
        'product', 'line', 'shift', 'operator'
    ).order_by('-analysis_datetime')[:10]
    
    context = {
        'total_analyses': total_analyses,
        'today_analyses': today_analyses,
        'analyses_by_product': list(analyses_by_product),
        'analyses_by_line': list(analyses_by_line),
        'recent_analyses': recent_analyses,
        'products_count': Product.objects.count(),
        'lines_count': ProductionLine.objects.count(),
        'properties_count': Property.objects.count(),
    }
    
    return render(request, 'quality_control/dashboard.html', context)

@csrf_exempt
@login_required
def reports_list_view(request):
    """Lista de laudos e relatórios"""
    
    # Análises por período
    analyses_by_month = SpotAnalysis.objects.extra(
        select={'month': "DATE_FORMAT(analysis_datetime, '%%Y-%%m')"}
    ).values('month').annotate(
        count=Count('id')
    ).order_by('-month')[:12]
    
    # Produtos mais analisados
    top_products = SpotAnalysis.objects.values(
        'product__name', 'product__code'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    context = {
        'analyses_by_month': list(analyses_by_month),
        'top_products': list(top_products),
        'total_analyses': SpotAnalysis.objects.count(),
    }
    
    return render(request, 'quality_control/reports_list.html', context)

@csrf_exempt
def get_product_properties(request):
    """API para obter propriedades de um produto"""
    product_id = request.GET.get('product_id')
    if not product_id:
        return JsonResponse({'error': 'Product ID required'}, status=400)
    
    try:
        product = Product.objects.get(id=product_id)
        specifications = Specification.objects.filter(product=product).select_related('property')
        
        properties = []
        for spec in specifications:
            properties.append({
                'id': spec.property.id,
                'name': spec.property.name,
                'unit': spec.property.unit,
                'type': spec.property.property_type,
                'min_value': float(spec.min_value) if spec.min_value else None,
                'max_value': float(spec.max_value) if spec.max_value else None,
                'target_value': float(spec.target_value) if spec.target_value else None,
            })
        
        return JsonResponse({
            'success': True,
            'properties': properties
        })
    
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def current_shift_api(request):
    """API para obter turno atual"""
    current_hour = timezone.now().hour
    
    if 6 <= current_hour < 18:
        shift_name = 'A'
        shift_description = 'Turno A (06:00 - 18:00)'
    else:
        shift_name = 'B'
        shift_description = 'Turno B (18:00 - 06:00)'
    
    try:
        shift = Shift.objects.get(name=shift_name)
        return JsonResponse({
            'success': True,
            'shift': {
                'id': shift.id,
                'name': shift.name,
                'description': shift_description,
                'start_time': shift.start_time.strftime('%H:%M'),
                'end_time': shift.end_time.strftime('%H:%M'),
            }
        })
    except Shift.DoesNotExist:
        return JsonResponse({
            'success': True,
            'shift': {
                'name': shift_name,
                'description': shift_description,
            }
        })

@csrf_exempt
def dashboard_data_api(request):
    """API para dados do dashboard"""
    
    # Dados dos últimos 30 dias
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Análises por dia
    daily_analyses = []
    for i in range(30):
        date = (timezone.now() - timedelta(days=i)).date()
        count = SpotAnalysis.objects.filter(analysis_datetime__date=date).count()
        daily_analyses.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    
    # Análises por produto
    product_analyses = SpotAnalysis.objects.filter(
        analysis_datetime__gte=thirty_days_ago
    ).values('product__name').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    return JsonResponse({
        'success': True,
        'daily_analyses': daily_analyses[::-1],  # Ordem cronológica
        'product_analyses': list(product_analyses),
        'total_analyses': SpotAnalysis.objects.count(),
        'today_analyses': SpotAnalysis.objects.filter(
            analysis_datetime__date=timezone.now().date()
        ).count(),
    })

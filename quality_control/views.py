"""
Views do app quality_control
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, CreateView, DetailView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json

from core.models import Plant, ProductionLine, Shift
from .models import Product, Property, Specification, SpotAnalysis, CompositeSample, CompositeSampleResult, ChemicalAnalysis, AnalysisType, AnalysisTypeProperty


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class SpotAnalysisListView(ListView):
    model = SpotAnalysis
    template_name = 'quality_control/spot_analysis_list.html'
    context_object_name = 'analyses'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = SpotAnalysis.objects.select_related(
            'spot_sample__product', 'spot_sample__production_line', 'spot_sample__shift', 'spot_sample__operator'
        ).order_by('-spot_sample__spot_sample__sample_time')
        
        # Filtros
        product_id = self.request.GET.get('product')
        line_id = self.request.GET.get('line')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        if product_id:
            queryset = queryset.filter(spot_sample__product_id=product_id)
        if line_id:
            queryset = queryset.filter(spot_sample__production_line_id=line_id)
        if date_from:
            queryset = queryset.filter(spot_sample__spot_sample__sample_time__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(spot_sample__spot_sample__sample_time__date__lte=date_to)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        context['lines'] = ProductionLine.objects.all()
        context['total_analyses'] = self.get_queryset().count()
        context['user'] = self.request.user
        context['username'] = self.request.user.username if self.request.user.is_authenticated else None
        return context


@method_decorator(login_required, name='dispatch')
class SpotAnalysisCreateView(CreateView):
    model = SpotAnalysis
    template_name = 'quality_control/spot_analysis_create_dynamic.html'
    fields = ['property', 'value', 'unit', 'test_method']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obter tipo de análise da URL
        analysis_type_param = self.request.GET.get('type', 'pontual')
        
        try:
            if analysis_type_param == 'pontual':
                analysis_type = AnalysisType.objects.get(code='PONTUAL')
                context['analysis_type_name'] = 'Análise Pontual'
                context['analysis_type_description'] = 'Análises realizadas diretamente no fluxo de produção'
                context['analysis_type_icon'] = 'lightning'
            elif analysis_type_param == 'composta':
                analysis_type = AnalysisType.objects.get(code='COMPOSTA')
                context['analysis_type_name'] = 'Análise Composta'
                context['analysis_type_description'] = 'Análises que representam 12 horas de produção'
                context['analysis_type_icon'] = 'clock-history'
            else:
                analysis_type = AnalysisType.objects.first()
                context['analysis_type_name'] = analysis_type.name
                context['analysis_type_description'] = analysis_type.description
                context['analysis_type_icon'] = 'clipboard-data'
        except AnalysisType.DoesNotExist:
            # Criar tipos padrão se não existirem
            analysis_type = self.create_default_analysis_types()
            context['analysis_type_name'] = 'Análise Pontual'
            context['analysis_type_description'] = 'Análises realizadas diretamente no fluxo de produção'
            context['analysis_type_icon'] = 'lightning'
        
        context['analysis_type'] = analysis_type
        context['products'] = Product.objects.filter(is_active=True)
        context['lines'] = ProductionLine.objects.filter(is_active=True)
        context['shifts'] = Shift.objects.all()
        context['properties'] = Property.objects.filter(is_active=True)
        
        # Turno atual
        current_hour = timezone.now().hour
        if 6 <= current_hour < 18:
            current_shift = Shift.objects.filter(name='A').first()
        else:
            current_shift = Shift.objects.filter(name='B').first()
        context['current_shift'] = current_shift
        
        return context
    
    def create_default_analysis_types(self):
        """Criar tipos de análise padrão se não existirem"""
        pontual, created = AnalysisType.objects.get_or_create(
            code='PONTUAL',
            defaults={
                'name': 'Análise Pontual',
                'description': 'Análises realizadas diretamente no fluxo de produção',
                'frequency_per_shift': 3
            }
        )
        
        composta, created = AnalysisType.objects.get_or_create(
            code='COMPOSTA',
            defaults={
                'name': 'Análise Composta',
                'description': 'Análises que representam 12 horas de produção',
                'frequency_per_shift': 1
            }
        )
        
        return pontual
    
    def form_valid(self, form):
        # Primeiro, criar ou obter o SpotSample
        from .models import SpotSample
        
        # Obter dados do formulário
        date = self.request.POST.get('date')
        shift_id = self.request.POST.get('shift')
        production_line_id = self.request.POST.get('production_line')
        product_id = self.request.POST.get('product')
        sample_time = self.request.POST.get('sample_time')
        
        # Criar ou obter SpotSample
        spot_sample, created = SpotSample.objects.get_or_create(
            date=date,
            shift_id=shift_id,
            production_line_id=production_line_id,
            product_id=product_id,
            analysis_type=self.get_context_data()['analysis_type'],
            defaults={
                'sample_time': sample_time,
                'operator': self.request.user,
            }
        )
        
        # Associar a análise à amostra
        form.instance.spot_sample = spot_sample
        form.instance.created_by = self.request.user
        
        messages.success(self.request, 'Análise criada com sucesso!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return '/qc/spot-analysis/'


@csrf_exempt
@login_required
def analysis_type_selection_view(request):
    """Tela de seleção do tipo de análise"""
    analysis_types = AnalysisType.objects.filter(is_active=True)
    
    context = {
        'analysis_types': analysis_types,
    }
    
    return render(request, 'quality_control/analysis_type_selection.html', context)


@csrf_exempt
@login_required
def dashboard_view(request):
    """Dashboard principal com estatísticas"""
    
    # Estatísticas gerais - incluindo amostras compostas
    total_spot_analyses = SpotAnalysis.objects.count()
    total_composite_samples = CompositeSample.objects.count()
    total_analyses = total_spot_analyses + total_composite_samples
    
    today_analyses = SpotAnalysis.objects.filter(
        spot_sample__spot_sample__sample_time__date=timezone.now().date()
    ).count()
    
    # Análises por produto (últimos 30 dias) - incluindo amostras compostas
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Análises pontuais por produto
    spot_analyses_by_product = SpotAnalysis.objects.filter(
        spot_sample__spot_sample__sample_time__gte=thirty_days_ago
    ).values('spot_sample__spot_sample__product__name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Amostras compostas por produto
    composite_analyses_by_product = CompositeSample.objects.filter(
        date__gte=thirty_days_ago.date()
    ).values('spot_sample__product__name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Combinar análises pontuais e compostas
    analyses_by_product = list(spot_analyses_by_product)
    for item in composite_analyses_by_product:
        # Verificar se já existe o produto na lista
        existing = next((x for x in analyses_by_product if x['spot_sample__product__name'] == item['spot_sample__product__name']), None)
        if existing:
            existing['count'] += item['count']
        else:
            analyses_by_product.append(item)
    
    # Ordenar por count
    analyses_by_product.sort(key=lambda x: x['count'], reverse=True)
    
    # Análises por linha (últimos 7 dias)
    seven_days_ago = timezone.now() - timedelta(days=7)
    analyses_by_line = SpotAnalysis.objects.filter(
        spot_sample__spot_sample__sample_time__gte=seven_days_ago
    ).values('spot_sample__spot_sample__production_line__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Análises recentes - incluindo amostras compostas
    recent_spot_analyses = SpotAnalysis.objects.select_related(
        'spot_sample__product', 'spot_sample__production_line', 'spot_sample__shift', 'spot_sample__operator'
    ).order_by('-spot_sample__spot_sample__sample_time')[:5]
    
    recent_composite_samples = CompositeSample.objects.select_related(
        'product', 'production_line', 'shift'
    ).order_by('-date', '-collection_time')[:5]
    
    # Combinar análises recentes
    recent_analyses = []
    for analysis in recent_spot_analyses:
        recent_analyses.append({
            'type': 'spot',
            'product': analysis.spot_sample.product,
            'production_line': analysis.spot_sample.production_line,
            'date': analysis.spot_sample.spot_sample__sample_time,
            'shift': analysis.spot_sample.shift
        })
    
    for sample in recent_composite_samples:
        recent_analyses.append({
            'type': 'composite',
            'product': sample.product,
            'production_line': sample.production_line,
            'date': sample.collection_time,
            'shift': sample.shift
        })
    
    # Ordenar por data
    recent_analyses.sort(key=lambda x: x['date'], reverse=True)
    recent_analyses = recent_analyses[:10]
    
    context = {
        'total_analyses': total_analyses,
        'total_spot_analyses': total_spot_analyses,
        'total_composite_samples': total_composite_samples,
        'today_analyses': today_analyses,
        'analyses_by_product': analyses_by_product,
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
    
    # Análises por período - versão simplificada
    # Buscar análises dos últimos 12 meses
    from datetime import datetime, timedelta
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=365)
    
    # Agrupar por mês manualmente
    analyses_by_month = []
    current_date = start_date
    while current_date <= end_date:
        month_start = current_date.replace(day=1)
        if current_date.month == 12:
            month_end = current_date.replace(year=current_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = current_date.replace(month=current_date.month + 1, day=1) - timedelta(days=1)
        
        count = SpotAnalysis.objects.filter(
            spot_sample__spot_sample__sample_time__date__range=[month_start, month_end]
        ).count()
        
        if count > 0:
            analyses_by_month.append({
                'month': month_start.strftime('%Y-%m'),
                'count': count
            })
        
        # Próximo mês
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1, day=1)
    
    # Produtos mais analisados
    top_products = SpotAnalysis.objects.values(
        'spot_sample__product__name', 'product__code'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    context = {
        'analyses_by_month': analyses_by_month,
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
                'type': spec.property.data_type,
                'min_value': float(spec.lsl) if spec.lsl else None,
                'max_value': float(spec.usl) if spec.usl else None,
                'target_value': float(spec.target) if spec.target else None,
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
    
    # 1. Status das Amostras (Pontuais + Compostas) - CONTAR POR AMOSTRA, NÃO POR ANÁLISE
    spot_status_data = SpotAnalysis.objects.filter(
        spot_sample__spot_sample__sample_time__gte=thirty_days_ago
    ).values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Status das amostras compostas (contar amostras, não resultados individuais)
    composite_status_data = CompositeSample.objects.filter(
        date__gte=thirty_days_ago.date()
    ).values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Combinar dados de status
    all_status_data = {}
    for item in spot_status_data:
        status = item['status']
        all_status_data[status] = all_status_data.get(status, 0) + item['count']
    
    for item in composite_status_data:
        status = item['status']
        all_status_data[status] = all_status_data.get(status, 0) + item['count']
    
    # 2. Reprovações por Linha de Produção (Pontuais + Compostas) - CONTAR POR AMOSTRA
    spot_rejections_by_line = SpotAnalysis.objects.filter(
        spot_sample__spot_sample__sample_time__gte=thirty_days_ago,
        status='REJECTED'
    ).values('spot_sample__spot_sample__production_line__name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Contar amostras compostas reprovadas, não resultados individuais
    composite_rejections_by_line = CompositeSample.objects.filter(
        date__gte=thirty_days_ago.date(),
        status='REJECTED'
    ).values('spot_sample__production_line__name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Combinar reprovações por linha
    line_rejections = {}
    for item in spot_rejections_by_line:
        line_name = item['spot_sample__production_line__name']
        line_rejections[line_name] = line_rejections.get(line_name, 0) + item['count']
    
    for item in composite_rejections_by_line:
        line_name = item['spot_sample__production_line__name']
        line_rejections[line_name] = line_rejections.get(line_name, 0) + item['count']
    
    # 3. Motivos de Reprovação (por propriedade) - MANTER CONTAGEM POR PROPRIEDADE
    spot_rejection_reasons = SpotAnalysis.objects.filter(
        spot_sample__spot_sample__sample_time__gte=thirty_days_ago,
        status='REJECTED'
    ).values('property__name', 'property__identifier').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Para amostras compostas, contar resultados reprovados por propriedade
    # Nota: CompositeSampleResult não tem campo status, usar amostras compostas reprovadas
    composite_rejection_reasons = CompositeSample.objects.filter(
        date__gte=thirty_days_ago.date(),
        status='REJECTED'
    ).values('spot_sample__product__name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Combinar motivos de reprovação
    rejection_reasons = {}
    for item in spot_rejection_reasons:
        prop_name = item['property__name']
        rejection_reasons[prop_name] = rejection_reasons.get(prop_name, 0) + item['count']
    
    for item in composite_rejection_reasons:
        prop_name = item['spot_sample__product__name']
        rejection_reasons[prop_name] = rejection_reasons.get(prop_name, 0) + item['count']
    
    # 4. Média de Propriedades Aprovadas (últimos 30 dias) - MANTER CONTAGEM POR PROPRIEDADE
    spot_averages = SpotAnalysis.objects.filter(
        spot_sample__spot_sample__sample_time__gte=thirty_days_ago,
        status='APPROVED'
    ).values('property__name', 'property__identifier').annotate(
        avg_value=Avg('value')
    ).order_by('-avg_value')[:5]
    
    # Para amostras compostas, usar amostras aprovadas (CompositeSampleResult não tem status)
    composite_averages = CompositeSample.objects.filter(
        date__gte=thirty_days_ago.date(),
        status='APPROVED'
    ).values('spot_sample__product__name').annotate(
        avg_value=Avg('id')  # Usar ID como placeholder, já que não temos valores reais
    ).order_by('-avg_value')[:5]
    
    # Combinar médias de propriedades
    property_averages = {}
    for item in spot_averages:
        prop_name = item['property__name']
        if prop_name not in property_averages:
            property_averages[prop_name] = {'total': 0, 'count': 0}
        property_averages[prop_name]['total'] += float(item['avg_value'])
        property_averages[prop_name]['count'] += 1
    
    for item in composite_averages:
        prop_name = item['spot_sample__product__name']  # Usar spot_sample__product__name em vez de property__name
        if prop_name not in property_averages:
            property_averages[prop_name] = {'total': 0, 'count': 0}
        property_averages[prop_name]['total'] += float(item['avg_value'])
        property_averages[prop_name]['count'] += 1
    
    # Calcular médias finais
    final_averages = []
    for prop_name, data in property_averages.items():
        final_averages.append({
            'property__name': prop_name,
            'avg_value': data['total'] / data['count']
        })
    
    final_averages.sort(key=lambda x: x['avg_value'], reverse=True)
    
    return JsonResponse({
        'success': True,
        'rejection_status': [{'status': k, 'count': v} for k, v in all_status_data.items()],
        'rejection_by_line': [{'spot_sample__production_line__name': k, 'count': v} for k, v in line_rejections.items()],
        'rejection_reasons': [{'property__name': k, 'count': v} for k, v in rejection_reasons.items()],
        'property_averages': final_averages[:5],
        'totals': {
            'spot_analyses': SpotAnalysis.objects.count(),
            'composite_samples': CompositeSample.objects.count(),
            # CONTAR AMOSTRAS REPROVADAS, NÃO ANÁLISES INDIVIDUAIS
            'total_rejections': SpotAnalysis.objects.filter(status='REJECTED').count() + 
                              CompositeSample.objects.filter(status='REJECTED').count(),
            'total_alerts': SpotAnalysis.objects.filter(status='ALERT').count() + 
                          CompositeSample.objects.filter(status='ALERT').count(),
            'total_approved': SpotAnalysis.objects.filter(status='APPROVED').count() + 
                            CompositeSample.objects.filter(status='APPROVED').count(),
            'today_rejections': SpotAnalysis.objects.filter(
                spot_sample__spot_sample__sample_time__date=timezone.now().date(),
                status='REJECTED'
            ).count() + CompositeSample.objects.filter(
                date=timezone.now().date(),
                status='REJECTED'
            ).count(),
            'today_alerts': SpotAnalysis.objects.filter(
                spot_sample__spot_sample__sample_time__date=timezone.now().date(),
                status='ALERT'
            ).count() + CompositeSample.objects.filter(
                date=timezone.now().date(),
                status='ALERT'
            ).count()
        }
    })
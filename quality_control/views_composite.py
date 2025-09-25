"""
Views para amostras compostas
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, DetailView
from django.utils.decorators import method_decorator
from django.utils import timezone
from datetime import datetime, time

from core.models import ProductionLine, Shift
from .models import Product, Property, CompositeSample, CompositeSampleResult, AnalysisType

@login_required
def composite_sample_list(request):
    """Lista de amostras compostas"""
    samples = CompositeSample.objects.select_related(
        'product', 'production_line', 'shift'
    ).order_by('-date', '-collection_time')
    
    # Filtros
    product_id = request.GET.get('product')
    line_id = request.GET.get('line')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if product_id:
        samples = samples.filter(product_id=product_id)
    if line_id:
        samples = samples.filter(production_line_id=line_id)
    if date_from:
        samples = samples.filter(date__gte=date_from)
    if date_to:
        samples = samples.filter(date__lte=date_to)
    
    context = {
        'samples': samples,
        'products': Product.objects.filter(is_active=True),
        'lines': ProductionLine.objects.filter(is_active=True),
        'total_samples': samples.count(),
    }
    
    return render(request, 'quality_control/composite_sample_list.html', context)

@login_required
def composite_sample_create(request):
    """Criar nova amostra composta"""
    if request.method == 'POST':
        try:
            # Obter dados do formulário
            product_id = request.POST.get('product')
            production_line_id = request.POST.get('production_line')
            shift_id = request.POST.get('shift')
            date = request.POST.get('date')
            collection_time = request.POST.get('collection_time')
            observations = request.POST.get('observations', '')
            
            # Criar amostra composta
            sample = CompositeSample.objects.create(
                product_id=product_id,
                production_line_id=production_line_id,
                shift_id=shift_id,
                date=date,
                collection_time=collection_time,
                observations=observations,
                status='APPROVED'
            )
            
            # Processar resultados das propriedades
            # Obter propriedades para amostra composta
            try:
                analysis_type = AnalysisType.objects.get(code='COMPOSTA')
                properties = Property.objects.filter(
                    is_active=True,
                    analysistypeproperty__analysis_type=analysis_type
                ).order_by('display_order')
            except AnalysisType.DoesNotExist:
                # Se não houver configuração específica, usar todas as propriedades ativas
                properties = Property.objects.filter(is_active=True).order_by('display_order')
            
            # Debug: imprimir propriedades encontradas
            print(f"DEBUG: Propriedades encontradas: {properties.count()}")
            
            for property in properties:
                value_key = f'property_{property.id}_value'
                method_key = f'property_{property.id}_method'
                
                print(f"DEBUG: Verificando {value_key}: {request.POST.get(value_key, 'NÃO ENCONTRADO')}")
                
                if value_key in request.POST and request.POST[value_key]:
                    try:
                        result = CompositeSampleResult.objects.create(
                            composite_sample=sample,
                            property=property,
                            value=request.POST[value_key],
                            test_method=request.POST.get(method_key, property.test_method or '')
                        )
                        print(f"DEBUG: Resultado criado para {property.identifier} com status: {result.status}")
                    except Exception as e:
                        print(f"DEBUG: Erro ao criar resultado para {property.identifier}: {e}")
            
            messages.success(request, 'Amostra composta criada com sucesso!')
            return redirect('quality_control:composite_sample_detail', sample_id=sample.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao criar amostra composta: {str(e)}')
    
    # Obter dados para o formulário
    products = Product.objects.filter(is_active=True).order_by('display_order')
    lines = ProductionLine.objects.filter(is_active=True).order_by('name')
    shifts = Shift.objects.all()
    
    # Obter propriedades para amostra composta
    try:
        analysis_type = AnalysisType.objects.get(code='COMPOSTA')
        properties = Property.objects.filter(
            is_active=True,
            analysistypeproperty__analysis_type=analysis_type
        ).order_by('display_order')
    except AnalysisType.DoesNotExist:
        # Se não houver configuração específica, usar todas as propriedades ativas
        properties = Property.objects.filter(is_active=True).order_by('display_order')
    
    context = {
        'products': products,
        'lines': lines,
        'shifts': shifts,
        'properties': properties,
    }
    
    return render(request, 'quality_control/composite_sample_create.html', context)

@login_required
def composite_sample_detail(request, sample_id):
    """Detalhes da amostra composta"""
    sample = get_object_or_404(CompositeSample, id=sample_id)
    results = CompositeSampleResult.objects.filter(composite_sample=sample).select_related('property')
    
    context = {
        'sample': sample,
        'results': results,
    }
    
    return render(request, 'quality_control/composite_sample_detail.html', context)

@login_required
def composite_sample_edit(request, sample_id):
    """Editar amostra composta"""
    sample = get_object_or_404(CompositeSample, id=sample_id)
    
    if request.method == 'POST':
        try:
            # Atualizar dados básicos
            sample.product_id = request.POST.get('product')
            sample.production_line_id = request.POST.get('production_line')
            sample.shift_id = request.POST.get('shift')
            sample.date = request.POST.get('date')
            sample.collection_time = request.POST.get('collection_time')
            sample.observations = request.POST.get('observations', '')
            sample.save()
            
            # Atualizar resultados
            results = CompositeSampleResult.objects.filter(composite_sample=sample)
            for result in results:
                value_key = f'property_{result.property.id}_value'
                method_key = f'property_{result.property.id}_method'
                
                if value_key in request.POST:
                    result.value = request.POST[value_key] or 0
                    result.test_method = request.POST.get(method_key, result.property.test_method)
                    result.save()
            
            messages.success(request, 'Amostra composta atualizada com sucesso!')
            return redirect('quality_control:composite_sample_detail', sample_id=sample.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar amostra composta: {str(e)}')
    
    # Obter dados para o formulário
    products = Product.objects.filter(is_active=True).order_by('display_order')
    lines = ProductionLine.objects.filter(is_active=True).order_by('name')
    shifts = Shift.objects.all()
    properties = Property.objects.filter(is_active=True).order_by('display_order')
    results = CompositeSampleResult.objects.filter(composite_sample=sample).select_related('property')
    
    context = {
        'sample': sample,
        'products': products,
        'lines': lines,
        'shifts': shifts,
        'properties': properties,
        'results': results,
    }
    
    return render(request, 'quality_control/composite_sample_edit.html', context)

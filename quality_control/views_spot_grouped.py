"""
Views para análises pontuais agrupadas por amostra
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from datetime import datetime, time

from core.models import ProductionLine, Shift
from .models import Product, Property, SpotAnalysis, AnalysisType, SpotSample


@login_required
def spot_sample_create(request):
    """Criar nova amostra pontual com múltiplas análises"""
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Obter dados básicos da amostra
                date = request.POST.get('date')
                product_id = request.POST.get('product')
                production_line_id = request.POST.get('production_line')
                shift_id = request.POST.get('shift')
                sample_time = request.POST.get('sample_time')
                sequence = request.POST.get('sequence')
                observations = request.POST.get('observations', '')
                
                # Validar dados obrigatórios
                if not all([date, product_id, production_line_id, shift_id, sample_time, sequence]):
                    messages.error(request, 'Por favor, preencha todos os campos obrigatórios.')
                    return redirect('quality_control:spot_sample_create')
                
                # Obter objetos relacionados
                product = get_object_or_404(Product, id=product_id)
                production_line = get_object_or_404(ProductionLine, id=production_line_id)
                shift = get_object_or_404(Shift, id=shift_id)
                analysis_type = get_object_or_404(AnalysisType, code='PONTUAL')
                
                # Verificar se já existe uma amostra com os mesmos dados
                existing_sample = SpotSample.objects.filter(
                    date=date,
                    shift=shift,
                    production_line=production_line,
                    product=product,
                    sequence=sequence
                ).first()
                
                if existing_sample:
                    messages.warning(request, 'Já existe uma amostra com esses dados. Deseja atualizá-la?')
                    return redirect('quality_control:spot_sample_edit', sample_id=existing_sample.id)
                
                # Criar a amostra pontual
                spot_sample = SpotSample.objects.create(
                    analysis_type=analysis_type,
                    date=date,
                    shift=shift,
                    production_line=production_line,
                    product=product,
                    sequence=sequence,
                    sample_time=sample_time,
                    operator=request.user,
                    observations=observations
                )
                
                # Processar análises das propriedades
                properties = Property.objects.filter(
                    is_active=True,
                    analysistypeproperty__analysis_type=analysis_type
                ).order_by('display_order')
                
                analyses_created = 0
                for property in properties:
                    value_key = f'property_{property.id}_value'
                    method_key = f'property_{property.id}_method'
                    
                    if value_key in request.POST and request.POST[value_key]:
                        try:
                            value_str = request.POST[value_key].strip()
                            if value_str:
                                # Converter valor para Decimal
                                from decimal import Decimal
                                value = Decimal(value_str.replace(',', '.'))
                                
                                # Criar análise
                                SpotAnalysis.objects.create(
                                    spot_sample=spot_sample,
                                    property=property,
                                    value=value,
                                    unit=property.unit,
                                    test_method=request.POST.get(method_key, property.test_method or 'Método padrão')
                                )
                                analyses_created += 1
                                
                        except (ValueError, Decimal.InvalidOperation) as e:
                            messages.warning(request, f'Valor inválido para {property.name}: {value_str}')
                        except Exception as e:
                            messages.warning(request, f'Erro ao processar {property.name}: {str(e)}')
                
                if analyses_created == 0:
                    messages.warning(request, 'Nenhuma análise foi registrada. A amostra foi criada mas está vazia.')
                else:
                    messages.success(request, f'Amostra pontual criada com sucesso! {analyses_created} análises registradas.')
                
                return redirect('quality_control:spot_sample_detail', sample_id=spot_sample.id)
                
        except Exception as e:
            messages.error(request, f'Erro ao criar amostra pontual: {str(e)}')
    
    # Obter dados para o formulário
    products = Product.objects.filter(is_active=True).order_by('display_order')
    lines = ProductionLine.objects.filter(is_active=True).order_by('name')
    shifts = Shift.objects.all()
    
    # Obter propriedades para análise pontual
    try:
        analysis_type = AnalysisType.objects.get(code='PONTUAL')
        properties = Property.objects.filter(
            is_active=True,
            analysistypeproperty__analysis_type=analysis_type
        ).order_by('display_order')
    except AnalysisType.DoesNotExist:
        properties = Property.objects.filter(is_active=True).order_by('display_order')
    
    context = {
        'products': products,
        'lines': lines,
        'shifts': shifts,
        'properties': properties,
    }
    
    return render(request, 'quality_control/spot_sample_create.html', context)


@login_required
def spot_sample_list(request):
    """Lista de amostras pontuais"""
    samples = SpotSample.objects.select_related(
        'product', 'shift', 'production_line', 'operator'
    ).prefetch_related('spotanalysis_set__property').order_by('-date', '-sample_time')
    
    context = {
        'samples': samples,
    }
    
    return render(request, 'quality_control/spot_sample_list.html', context)


@login_required
def spot_sample_detail(request, sample_id):
    """Detalhes de uma amostra pontual"""
    sample = get_object_or_404(
        SpotSample.objects.select_related(
            'product', 'shift', 'production_line', 'operator'
        ).prefetch_related('spotanalysis_set__property'),
        id=sample_id
    )
    
    analyses = sample.spotanalysis_set.all().order_by('property__display_order')
    
    context = {
        'sample': sample,
        'analyses': analyses,
    }
    
    return render(request, 'quality_control/spot_sample_detail.html', context)


@login_required
def spot_sample_edit(request, sample_id):
    """Editar uma amostra pontual"""
    sample = get_object_or_404(
        SpotSample.objects.select_related(
            'product', 'shift', 'production_line', 'operator'
        ).prefetch_related('spotanalysis_set__property'),
        id=sample_id
    )
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Atualizar dados básicos da amostra
                sample.observations = request.POST.get('observations', '')
                sample.save()
                
                # Processar análises das propriedades
                properties = Property.objects.filter(
                    is_active=True,
                    analysistypeproperty__analysis_type=sample.analysis_type
                ).order_by('display_order')
                
                analyses_updated = 0
                for property in properties:
                    value_key = f'property_{property.id}_value'
                    method_key = f'property_{property.id}_method'
                    
                    if value_key in request.POST and request.POST[value_key]:
                        try:
                            value_str = request.POST[value_key].strip()
                            if value_str:
                                from decimal import Decimal
                                value = Decimal(value_str.replace(',', '.'))
                                
                                # Buscar ou criar análise
                                analysis, created = SpotAnalysis.objects.get_or_create(
                                    spot_sample=sample,
                                    property=property,
                                    defaults={
                                        'value': value,
                                        'unit': property.unit,
                                        'test_method': property.test_method or 'Método padrão'
                                    }
                                )
                                
                                if not created:
                                    analysis.value = value
                                    analysis.test_method = request.POST.get(method_key, property.test_method or 'Método padrão')
                                    analysis.save()
                                
                                analyses_updated += 1
                                
                        except (ValueError, Decimal.InvalidOperation) as e:
                            messages.warning(request, f'Valor inválido para {property.name}: {value_str}')
                        except Exception as e:
                            messages.warning(request, f'Erro ao processar {property.name}: {str(e)}')
                
                messages.success(request, f'Amostra pontual atualizada com sucesso! {analyses_updated} análises processadas.')
                return redirect('quality_control:spot_sample_detail', sample_id=sample.id)
                
        except Exception as e:
            messages.error(request, f'Erro ao atualizar amostra pontual: {str(e)}')
    
    # Obter análises existentes
    existing_analyses = {a.property.id: a for a in sample.spotanalysis_set.all()}
    
    # Obter propriedades para análise pontual
    try:
        analysis_type = sample.analysis_type
        properties = Property.objects.filter(
            is_active=True,
            analysistypeproperty__analysis_type=analysis_type
        ).order_by('display_order')
    except:
        properties = Property.objects.filter(is_active=True).order_by('display_order')
    
    context = {
        'sample': sample,
        'properties': properties,
        'existing_analyses': existing_analyses,
    }
    
    return render(request, 'quality_control/spot_sample_edit.html', context)


@login_required
def spot_sample_delete(request, sample_id):
    """Excluir uma amostra pontual"""
    sample = get_object_or_404(SpotSample, id=sample_id)
    
    if request.method == 'POST':
        try:
            sample.delete()
            messages.success(request, 'Amostra pontual excluída com sucesso!')
            return redirect('quality_control:spot_sample_list')
        except Exception as e:
            messages.error(request, f'Erro ao excluir amostra pontual: {str(e)}')
    
    context = {
        'sample': sample,
    }
    
    return render(request, 'quality_control/spot_sample_delete.html', context)

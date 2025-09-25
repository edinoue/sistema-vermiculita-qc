"""
Views melhoradas para análises pontuais
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, time

from core.models import ProductionLine, Shift
from .models import Product, Property, SpotAnalysis, AnalysisType

@login_required
def spot_analysis_create_improved(request):
    """Criação melhorada de análise pontual"""
    if request.method == 'POST':
        try:
            # Obter dados básicos
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
                return redirect('quality_control:spot_analysis_create_improved')
            
            # Obter objetos relacionados
            product = get_object_or_404(Product, id=product_id)
            production_line = get_object_or_404(ProductionLine, id=production_line_id)
            shift = get_object_or_404(Shift, id=shift_id)
            analysis_type = get_object_or_404(AnalysisType, code='PONTUAL')
            
            # Processar propriedades
            # Obter propriedades para análise pontual
            analysis_type = AnalysisType.objects.get(code='PONTUAL')
            properties = Property.objects.filter(
                is_active=True,
                analysistypeproperty__analysis_type=analysis_type
            ).order_by('display_order')
            created_analyses = []
            
            for property in properties:
                value_key = f'property_{property.id}_value'
                method_key = f'property_{property.id}_method'
                
                # Verificar se há valor para esta propriedade
                if value_key in request.POST and request.POST[value_key]:
                    try:
                        value = float(request.POST[value_key])
                        test_method = request.POST.get(method_key, property.test_method or 'Método padrão')
                        
                        # Criar análise para esta propriedade
                        analysis = SpotAnalysis.objects.create(
                            analysis_type=analysis_type,
                            date=date,
                            product=product,
                            production_line=production_line,
                            shift=shift,
                            sample_time=sample_time,
                            sequence=sequence,
                            property=property,
                            value=value,
                            unit=property.unit,
                            test_method=test_method,
                            status='APPROVED'  # Status será calculado automaticamente
                        )
                        
                        # O status será calculado automaticamente pelo método save() do modelo
                        print(f"DEBUG: Análise criada com status: {analysis.status}")
                        created_analyses.append(analysis)
                        
                    except ValueError:
                        messages.warning(request, f'Valor inválido para {property.name}. Ignorando.')
                        continue
            
            if created_analyses:
                messages.success(request, f'Análise pontual criada com sucesso! {len(created_analyses)} propriedades registradas.')
                return redirect('quality_control:spot_analysis_list')
            else:
                messages.warning(request, 'Nenhuma propriedade foi preenchida. Análise não foi criada.')
                return redirect('quality_control:spot_analysis_create_improved')
            
        except Exception as e:
            messages.error(request, f'Erro ao criar análise pontual: {str(e)}')
            return redirect('quality_control:spot_analysis_create_improved')
    
    # Obter dados para o formulário
    products = Product.objects.filter(is_active=True).order_by('display_order')
    lines = ProductionLine.objects.filter(is_active=True).order_by('name')
    shifts = Shift.objects.all()
    # Obter propriedades para análise pontual
    analysis_type = AnalysisType.objects.get(code='PONTUAL')
    properties = Property.objects.filter(
        is_active=True,
        analysistypeproperty__analysis_type=analysis_type
    ).order_by('display_order')
    
    context = {
        'products': products,
        'lines': lines,
        'shifts': shifts,
        'properties': properties,
    }
    
    return render(request, 'quality_control/spot_analysis_create_improved.html', context)

@login_required
def spot_analysis_edit_improved(request, analysis_id):
    """Edição melhorada de análise pontual"""
    analysis = get_object_or_404(SpotAnalysis, id=analysis_id)
    
    if request.method == 'POST':
        try:
            # Atualizar dados básicos
            analysis.date = request.POST.get('date')
            analysis.product_id = request.POST.get('product')
            analysis.production_line_id = request.POST.get('production_line')
            analysis.shift_id = request.POST.get('shift')
            analysis.sample_time = request.POST.get('sample_time')
            analysis.sequence = request.POST.get('sequence')
            analysis.save()
            
            # Atualizar propriedades
            # Obter propriedades para análise pontual
            analysis_type = AnalysisType.objects.get(code='PONTUAL')
            properties = Property.objects.filter(
                is_active=True,
                analysistypeproperty__analysis_type=analysis_type
            ).order_by('display_order')
            for property in properties:
                value_key = f'property_{property.id}_value'
                method_key = f'property_{property.id}_method'
                
                if value_key in request.POST:
                    try:
                        value = float(request.POST[value_key]) if request.POST[value_key] else 0
                        test_method = request.POST.get(method_key, property.test_method or 'Método padrão')
                        
                        # Atualizar ou criar análise para esta propriedade
                        property_analysis, created = SpotAnalysis.objects.get_or_create(
                            analysis_type=analysis.analysis_type,
                            date=analysis.date,
                            product=analysis.product,
                            production_line=analysis.production_line,
                            shift=analysis.shift,
                            sample_time=analysis.sample_time,
                            sequence=analysis.sequence,
                            property=property,
                            defaults={
                                'value': value,
                                'unit': property.unit,
                                'test_method': test_method,
                                'status': 'PENDENTE'
                            }
                        )
                        
                        if not created:
                            property_analysis.value = value
                            property_analysis.test_method = test_method
                            property_analysis.save()
                        
                    except ValueError:
                        messages.warning(request, f'Valor inválido para {property.name}. Ignorando.')
                        continue
            
            messages.success(request, 'Análise pontual atualizada com sucesso!')
            return redirect('quality_control:spot_analysis_list')
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar análise pontual: {str(e)}')
    
    # Obter dados para o formulário
    products = Product.objects.filter(is_active=True).order_by('display_order')
    lines = ProductionLine.objects.filter(is_active=True).order_by('name')
    shifts = Shift.objects.all()
    # Obter propriedades para análise pontual
    analysis_type = AnalysisType.objects.get(code='PONTUAL')
    properties = Property.objects.filter(
        is_active=True,
        analysistypeproperty__analysis_type=analysis_type
    ).order_by('display_order')
    
    # Obter análises existentes para esta amostra
    existing_analyses = SpotAnalysis.objects.filter(
        analysis_type=analysis.analysis_type,
        date=analysis.date,
        product=analysis.product,
        production_line=analysis.production_line,
        shift=analysis.shift,
        sample_time=analysis.sample_time,
        sequence=analysis.sequence
    ).select_related('property')
    
    # Criar dicionário de valores existentes
    existing_values = {}
    for existing in existing_analyses:
        existing_values[existing.property.id] = {
            'value': existing.value,
            'method': existing.test_method
        }
    
    context = {
        'analysis': analysis,
        'products': products,
        'lines': lines,
        'shifts': shifts,
        'properties': properties,
        'existing_values': existing_values,
    }
    
    return render(request, 'quality_control/spot_analysis_edit_improved.html', context)

@login_required
def spot_analysis_detail_improved(request, analysis_id):
    """Detalhes melhorados de análise pontual"""
    analysis = get_object_or_404(SpotAnalysis, id=analysis_id)
    
    # Obter todas as análises relacionadas (mesma amostra)
    related_analyses = SpotAnalysis.objects.filter(
        analysis_type=analysis.analysis_type,
        date=analysis.date,
        product=analysis.product,
        production_line=analysis.production_line,
        shift=analysis.shift,
        sample_time=analysis.sample_time,
        sequence=analysis.sequence
    ).select_related('property').order_by('property__display_order')
    
    context = {
        'analysis': analysis,
        'related_analyses': related_analyses,
    }
    
    return render(request, 'quality_control/spot_analysis_detail_improved.html', context)

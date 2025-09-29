"""
Views para o novo sistema de análise pontual
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db import transaction

from core.models import ProductionLine, Shift
from .models import Product, Property, AnalysisType
from .models_production import (
    ProductionRegistration,
    SpotAnalysisRegistration,
    SpotAnalysisPropertyResult
)

@login_required
def spot_analysis_new_create(request):
    """Criar nova análise pontual com novo sistema"""
    
    # Obter produção ativa do turno atual
    current_time = timezone.now()
    current_shift = None
    
    if 6 <= current_time.hour < 14:
        current_shift = Shift.objects.filter(name__icontains='manhã').first()
    elif 14 <= current_time.hour < 22:
        current_shift = Shift.objects.filter(name__icontains='tarde').first()
    else:
        current_shift = Shift.objects.filter(name__icontains='noite').first()
    
    if not current_shift:
        current_shift = Shift.objects.first()
    
    # Buscar produção ativa
    production = ProductionRegistration.objects.filter(
        date=timezone.now().date(),
        shift=current_shift,
        status='ACTIVE'
    ).first()
    
    if not production:
        messages.error(request, 'Nenhuma produção cadastrada para o turno atual. Cadastre a produção primeiro.')
        return redirect('quality_control:production_registration_create')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Obter dados do formulário
                pontual_number = int(request.POST.get('pontual_number'))
                production_line_id = request.POST.get('production_line')
                product_id = request.POST.get('product')
                
                # Verificar se já existe análise para esta pontual
                existing_analysis = SpotAnalysisRegistration.objects.filter(
                    production=production,
                    production_line_id=production_line_id,
                    product_id=product_id,
                    pontual_number=pontual_number
                ).first()
                
                if existing_analysis:
                    messages.error(request, f'Já existe uma análise para a pontual {pontual_number} deste produto.')
                    return redirect('quality_control:spot_analysis_new_create')
                
                # Obter tipo de análise pontual
                analysis_type = AnalysisType.objects.get(code='PONTUAL')
                
                # Criar registro de análise
                analysis = SpotAnalysisRegistration.objects.create(
                    production=production,
                    date=timezone.now().date(),
                    shift=current_shift,
                    production_line_id=production_line_id,
                    product_id=product_id,
                    analysis_type=analysis_type,
                    pontual_number=pontual_number,
                    operator=request.user
                )
                
                # Processar resultados das propriedades
                properties = Property.objects.filter(
                    is_active=True,
                    analysistypeproperty__analysis_type=analysis_type
                ).order_by('display_order')
                
                approved_count = 0
                total_count = 0
                
                for property in properties:
                    value_key = f'property_{property.id}_value'
                    method_key = f'property_{property.id}_method'
                    
                    if value_key in request.POST and request.POST[value_key]:
                        try:
                            value = float(request.POST[value_key])
                            test_method = request.POST.get(method_key, property.test_method or 'Método padrão')
                            
                            # Criar resultado da propriedade
                            SpotAnalysisPropertyResult.objects.create(
                                analysis=analysis,
                                property=property,
                                value=value,
                                unit=property.unit,
                                test_method=test_method
                            )
                            
                            # Verificar se está dentro da especificação
                            if hasattr(property, 'specification') and property.specification:
                                spec = property.specification
                                if spec.lsl is not None and value < spec.lsl:
                                    # Fora da especificação (muito baixo)
                                    pass
                                elif spec.usl is not None and value > spec.usl:
                                    # Fora da especificação (muito alto)
                                    pass
                                else:
                                    # Dentro da especificação
                                    approved_count += 1
                            
                            total_count += 1
                            
                        except ValueError:
                            messages.warning(request, f'Valor inválido para {property.name}. Ignorando.')
                            continue
                
                # Determinar resultado da análise
                if total_count > 0:
                    if approved_count == total_count:
                        analysis.analysis_result = 'APPROVED'
                    else:
                        analysis.analysis_result = 'REJECTED'
                else:
                    analysis.analysis_result = 'PENDING'
                
                analysis.save()
                
                messages.success(request, f'Análise pontual {pontual_number} registrada com sucesso!')
                return redirect('quality_control:spot_analysis_new_list')
                
        except Exception as e:
            messages.error(request, f'Erro ao criar análise pontual: {str(e)}')
    
    # Obter dados para o formulário
    lines = production.productionlines.filter(is_active=True)
    products = production.products.filter(is_active=True)
    
    # Obter propriedades para análise pontual
    analysis_type = AnalysisType.objects.get(code='PONTUAL')
    properties = Property.objects.filter(
        is_active=True,
        analysistypeproperty__analysis_type=analysis_type
    ).order_by('display_order')
    
    context = {
        'production': production,
        'lines': lines,
        'products': products,
        'properties': properties,
        'current_shift': current_shift,
        'today': timezone.now().date(),
    }
    
    return render(request, 'quality_control/spot_analysis_new_create.html', context)

@login_required
def spot_analysis_new_list(request):
    """Lista de análises pontuais do novo sistema"""
    analyses = SpotAnalysisRegistration.objects.all().order_by('-date', '-created_at')
    
    context = {
        'analyses': analyses,
    }
    
    return render(request, 'quality_control/spot_analysis_new_list.html', context)

@login_required
def spot_analysis_new_detail(request, analysis_id):
    """Detalhes da análise pontual"""
    analysis = get_object_or_404(SpotAnalysisRegistration, id=analysis_id)
    property_results = analysis.property_results.all()
    
    context = {
        'analysis': analysis,
        'property_results': property_results,
    }
    
    return render(request, 'quality_control/spot_analysis_new_detail.html', context)

@login_required
def spot_analysis_new_edit(request, analysis_id):
    """Editar análise pontual"""
    analysis = get_object_or_404(SpotAnalysisRegistration, id=analysis_id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Atualizar dados básicos
                analysis.pontual_number = int(request.POST.get('pontual_number'))
                analysis.production_line_id = request.POST.get('production_line')
                analysis.product_id = request.POST.get('product')
                
                # Atualizar resultados das propriedades
                analysis.property_results.all().delete()
                
                properties = Property.objects.filter(
                    is_active=True,
                    analysistypeproperty__analysis_type=analysis.analysis_type
                ).order_by('display_order')
                
                approved_count = 0
                total_count = 0
                
                for property in properties:
                    value_key = f'property_{property.id}_value'
                    method_key = f'property_{property.id}_method'
                    
                    if value_key in request.POST and request.POST[value_key]:
                        try:
                            value = float(request.POST[value_key])
                            test_method = request.POST.get(method_key, property.test_method or 'Método padrão')
                            
                            SpotAnalysisPropertyResult.objects.create(
                                analysis=analysis,
                                property=property,
                                value=value,
                                unit=property.unit,
                                test_method=test_method
                            )
                            
                            # Verificar especificação
                            if hasattr(property, 'specification') and property.specification:
                                spec = property.specification
                                if (spec.lsl is None or value >= spec.lsl) and (spec.usl is None or value <= spec.usl):
                                    approved_count += 1
                            
                            total_count += 1
                            
                        except ValueError:
                            messages.warning(request, f'Valor inválido para {property.name}. Ignorando.')
                            continue
                
                # Atualizar resultado da análise
                if total_count > 0:
                    if approved_count == total_count:
                        analysis.analysis_result = 'APPROVED'
                    else:
                        analysis.analysis_result = 'REJECTED'
                else:
                    analysis.analysis_result = 'PENDING'
                
                analysis.save()
                
                messages.success(request, 'Análise pontual atualizada com sucesso!')
                return redirect('quality_control:spot_analysis_new_detail', analysis_id=analysis.id)
                
        except Exception as e:
            messages.error(request, f'Erro ao atualizar análise pontual: {str(e)}')
    
    # Obter dados para o formulário
    lines = analysis.production.productionlines.filter(is_active=True)
    products = analysis.production.products.filter(is_active=True)
    properties = Property.objects.filter(
        is_active=True,
        analysistypeproperty__analysis_type=analysis.analysis_type
    ).order_by('display_order')
    
    # Obter valores atuais
    current_results = {pr.property_id: pr for pr in analysis.property_results.all()}
    
    context = {
        'analysis': analysis,
        'lines': lines,
        'products': products,
        'properties': properties,
        'current_results': current_results,
    }
    
    return render(request, 'quality_control/spot_analysis_new_edit.html', context)

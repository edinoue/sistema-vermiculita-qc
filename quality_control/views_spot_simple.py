"""
Views simplificadas para teste do sistema de análise pontual
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction

from core.models import ProductionLine, Shift
from .models import Product, Property, AnalysisType
from .models_production import (
    ProductionRegistration,
    SpotAnalysisRegistration,
    SpotAnalysisPropertyResult
)

@login_required
def spot_analysis_simple_create(request):
    """Criar nova análise pontual - versão simplificada"""
    
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
                            
                        except ValueError:
                            messages.warning(request, f'Valor inválido para {property.name}. Ignorando.')
                            continue
                
                # Definir resultado da análise
                analysis.analysis_result = 'APPROVED'
                analysis.save()
                
                messages.success(request, f'Análise pontual {pontual_number} registrada com sucesso!')
                return redirect('quality_control:spot_analysis_new_list')
                
        except Exception as e:
            messages.error(request, f'Erro ao criar análise pontual: {str(e)}')
    
    # Obter dados para o formulário
    lines = production.productionlines.filter(is_active=True)
    products = production.products.filter(is_active=True)
    
    # Obter propriedades
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
        'current_shift': current_shift
    }
    
    return render(request, 'quality_control/spot_analysis_simple_create.html', context)

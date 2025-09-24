"""
Views corrigidas para análises pontuais
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
def spot_analysis_create_fixed(request):
    """Criação corrigida de análise pontual"""
    if request.method == 'POST':
        try:
            # Obter dados do formulário
            date = request.POST.get('date')
            product_id = request.POST.get('product')
            production_line_id = request.POST.get('production_line')
            shift_id = request.POST.get('shift')
            sample_time = request.POST.get('sample_time')
            sequence = request.POST.get('sequence')
            
            # Criar análise pontual
            analysis = SpotAnalysis.objects.create(
                analysis_type=AnalysisType.objects.get(code='PONTUAL'),
                date=date,
                product_id=product_id,
                production_line_id=production_line_id,
                shift_id=shift_id,
                sample_time=sample_time,
                sequence=sequence,
                property=Property.objects.first(),  # Propriedade padrão
                value=0,  # Será atualizado com os resultados
                unit='%',
                test_method='Método padrão',
                status='PENDENTE'
            )
            
            # Processar resultados das propriedades
            # Obter propriedades para análise pontual
            analysis_type = AnalysisType.objects.get(code='PONTUAL')
            properties = Property.objects.filter(
                is_active=True,
                analysistypeproperty__analysis_type=analysis_type
            ).order_by('display_order')
            for property in properties:
                value_key = f'property_{property.id}_value'
                method_key = f'property_{property.id}_method'
                
                if value_key in request.POST and request.POST[value_key]:
                    # Criar nova análise para cada propriedade
                    SpotAnalysis.objects.create(
                        analysis_type=AnalysisType.objects.get(code='PONTUAL'),
                        date=date,
                        product_id=product_id,
                        production_line_id=production_line_id,
                        shift_id=shift_id,
                        sample_time=sample_time,
                        sequence=sequence,
                        property=property,
                        value=request.POST[value_key],
                        unit=property.unit,
                        test_method=request.POST.get(method_key, property.test_method),
                        status='PENDENTE'
                    )
            
            messages.success(request, 'Análise pontual criada com sucesso!')
            return redirect('quality_control:spot_analysis_list')
            
        except Exception as e:
            messages.error(request, f'Erro ao criar análise pontual: {str(e)}')
    
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
    
    return render(request, 'quality_control/spot_analysis_create_fixed.html', context)

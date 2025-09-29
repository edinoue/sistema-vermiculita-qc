"""
Views para cadastro de produção
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
    ProductionLineRegistration, 
    ProductionProductRegistration
)

@login_required
def production_registration_list(request):
    """Lista de cadastros de produção"""
    productions = ProductionRegistration.objects.all().order_by('-date', '-created_at')
    
    context = {
        'productions': productions,
    }
    
    return render(request, 'quality_control/production_registration_list.html', context)

@login_required
def production_registration_create(request):
    """Criar novo cadastro de produção"""
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Obter dados do formulário
                date = request.POST.get('date')
                shift_id = request.POST.get('shift')
                observations = request.POST.get('observations', '')
                
                # Verificar se já existe produção para esta data/turno
                existing = ProductionRegistration.objects.filter(
                    date=date,
                    shift_id=shift_id
                ).first()
                
                if existing:
                    messages.error(request, 'Já existe um cadastro de produção para esta data e turno.')
                    return redirect('quality_control:production_registration_create')
                
                # Criar cadastro de produção
                production = ProductionRegistration.objects.create(
                    date=date,
                    shift_id=shift_id,
                    operator=request.user,
                    observations=observations
                )
                
                # Processar linhas de produção selecionadas
                selected_lines = request.POST.getlist('production_lines')
                for line_id in selected_lines:
                    ProductionLineRegistration.objects.create(
                        production=production,
                        production_line_id=line_id
                    )
                
                # Processar produtos selecionados
                selected_products = request.POST.getlist('products')
                for product_id in selected_products:
                    product_type = request.POST.get(f'product_type_{product_id}', '')
                    ProductionProductRegistration.objects.create(
                        production=production,
                        product_id=product_id,
                        product_type=product_type
                    )
                
                messages.success(request, 'Cadastro de produção criado com sucesso!')
                return redirect('quality_control:production_registration_detail', production_id=production.id)
                
        except Exception as e:
            messages.error(request, f'Erro ao criar cadastro de produção: {str(e)}')
    
    # Obter dados para o formulário
    shifts = Shift.objects.all()
    production_lines = ProductionLine.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)
    
    context = {
        'shifts': shifts,
        'production_lines': production_lines,
        'products': products,
        'today': timezone.now().date(),
    }
    
    return render(request, 'quality_control/production_registration_create.html', context)

@login_required
def production_registration_detail(request, production_id):
    """Detalhes do cadastro de produção"""
    production = get_object_or_404(ProductionRegistration, id=production_id)
    
    # Obter linhas e produtos registrados
    lines = production.productionlines.all()
    products = production.products.all()
    
    context = {
        'production': production,
        'lines': lines,
        'products': products,
    }
    
    return render(request, 'quality_control/production_registration_detail.html', context)

@login_required
def production_registration_edit(request, production_id):
    """Editar cadastro de produção"""
    production = get_object_or_404(ProductionRegistration, id=production_id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Atualizar dados básicos
                production.date = request.POST.get('date')
                production.shift_id = request.POST.get('shift')
                production.observations = request.POST.get('observations', '')
                production.save()
                
                # Atualizar linhas de produção
                production.productionlines.all().delete()
                selected_lines = request.POST.getlist('production_lines')
                for line_id in selected_lines:
                    ProductionLineRegistration.objects.create(
                        production=production,
                        production_line_id=line_id
                    )
                
                # Atualizar produtos
                production.products.all().delete()
                selected_products = request.POST.getlist('products')
                for product_id in selected_products:
                    product_type = request.POST.get(f'product_type_{product_id}', '')
                    ProductionProductRegistration.objects.create(
                        production=production,
                        product_id=product_id,
                        product_type=product_type
                    )
                
                messages.success(request, 'Cadastro de produção atualizado com sucesso!')
                return redirect('quality_control:production_registration_detail', production_id=production.id)
                
        except Exception as e:
            messages.error(request, f'Erro ao atualizar cadastro de produção: {str(e)}')
    
    # Obter dados para o formulário
    shifts = Shift.objects.all()
    production_lines = ProductionLine.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)
    
    # Obter seleções atuais
    selected_lines = production.productionlines.values_list('production_line_id', flat=True)
    selected_products = production.products.all()
    
    context = {
        'production': production,
        'shifts': shifts,
        'production_lines': production_lines,
        'products': products,
        'selected_lines': selected_lines,
        'selected_products': selected_products,
    }
    
    return render(request, 'quality_control/production_registration_edit.html', context)

@login_required
def get_active_production(request):
    """API para obter produção ativa do turno atual"""
    try:
        # Obter turno atual
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
        
        # Buscar produção ativa para hoje e turno atual
        production = ProductionRegistration.objects.filter(
            date=timezone.now().date(),
            shift=current_shift,
            status='ACTIVE'
        ).first()
        
        if not production:
            return JsonResponse({'error': 'Nenhuma produção ativa encontrada'}, status=404)
        
        # Obter dados da produção
        lines = production.productionlines.filter(is_active=True).values(
            'id', 'production_line__id', 'production_line__name'
        )
        products = production.products.filter(is_active=True).values(
            'id', 'product__id', 'product__name', 'product_type'
        )
        
        return JsonResponse({
            'production_id': production.id,
            'date': production.date.strftime('%Y-%m-%d'),
            'shift': production.shift.name,
            'lines': list(lines),
            'products': list(products),
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

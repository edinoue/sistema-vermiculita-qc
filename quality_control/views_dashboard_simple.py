"""
View simplificada para o dashboard por linha de produção
Busca diretamente os dados existentes sem depender de cadastros de produção
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Count, Q
from core.models import Shift, Plant, ProductionLine
from quality_control.models import Property, SpotSample, SpotAnalysis, Product


@csrf_exempt
@login_required
def spot_dashboard_by_line_view_simple(request):
    """
    Dashboard de amostras pontuais por linha de produção - VERSÃO SIMPLIFICADA
    Busca diretamente os dados existentes sem depender de cadastros de produção
    """
    print("🔍 DEBUG: Iniciando dashboard simplificado")
    
    # Obter turno atual
    current_time = timezone.now()
    current_shift = None
    
    # Lógica para determinar o turno atual baseado no horário
    if 6 <= current_time.hour < 18:
        current_shift = Shift.objects.filter(name='A').first()
    else:
        current_shift = Shift.objects.filter(name='B').first()
    
    if not current_shift:
        current_shift = Shift.objects.first()
    
    # Garantir que temos um turno válido
    if not current_shift:
        current_shift = Shift.objects.create(
            name='A',
            start_time='06:00',
            end_time='18:00'
        )
    
    print(f"🔍 DEBUG: Turno atual: {current_shift}")
    
    # Obter todas as propriedades ativas
    properties = Property.objects.filter(is_active=True).order_by('display_order')
    print(f"🔍 DEBUG: Propriedades encontradas: {properties.count()}")
    
    # Buscar TODAS as amostras pontuais existentes
    today = timezone.now().date()
    all_samples = SpotSample.objects.filter(date=today).select_related(
        'product', 'production_line', 'production_line__plant', 'shift'
    ).order_by('production_line', 'product', '-sample_sequence')
    
    print(f"🔍 DEBUG: Amostras encontradas hoje: {all_samples.count()}")
    
    # Organizar dados por linha de produção
    lines_data = {}
    
    for sample in all_samples:
        line = sample.production_line
        plant = line.plant
        
        # Criar chave única para a linha
        line_key = f"{line.id}_{plant.id}"
        
        if line_key not in lines_data:
            lines_data[line_key] = {
                'line': line,
                'plant': plant,
                'products': {}
            }
        
        # Organizar por produto
        product_key = sample.product.id
        if product_key not in lines_data[line_key]['products']:
            lines_data[line_key]['products'][product_key] = {
                'product': sample.product,
                'sample': sample,
                'analyses': [],
                'property_analyses': {},
                'status': 'PENDENTE',
                'sequence': sample.sample_sequence,
                'observations': sample.observations,
                'sample_time': sample.sample_time
            }
        
        # Buscar análises desta amostra
        analyses = SpotAnalysis.objects.filter(
            spot_sample=sample
        ).select_related('property').order_by('property__display_order')
        
        print(f"🔍 DEBUG: Amostra {sample.id} - {analyses.count()} análises")
        
        # Organizar análises por propriedade
        property_analyses = {}
        for analysis in analyses:
            property_analyses[analysis.property_id] = analysis
            print(f"  - {analysis.property.name}: {analysis.value} {analysis.property.unit} ({analysis.status})")
        
        # Calcular status geral da amostra
        sample_status = 'APPROVED'
        has_rejected = analyses.filter(status='REJECTED').exists()
        has_alert = analyses.filter(status='ALERT').exists()
        
        if has_rejected:
            sample_status = 'REJECTED'
        elif has_alert:
            sample_status = 'ALERT'
        
        # Atualizar dados do produto
        lines_data[line_key]['products'][product_key].update({
            'sample': sample,
            'analyses': analyses,
            'property_analyses': property_analyses,
            'status': sample_status,
            'sequence': sample.sample_sequence,
            'observations': sample.observations,
            'sample_time': sample.sample_time
        })
    
    # Converter para lista
    lines_list = []
    for line_data in lines_data.values():
        # Converter produtos para lista
        products_list = list(line_data['products'].values())
        line_data['products'] = products_list
        lines_list.append(line_data)
    
    print(f"🔍 DEBUG: Linhas processadas: {len(lines_list)}")
    
    # Se não há dados, buscar produtos sem amostras
    if not lines_list:
        print("🔍 DEBUG: Nenhuma amostra encontrada, buscando produtos sem amostras")
        
        # Buscar todas as linhas ativas
        all_lines = ProductionLine.objects.filter(is_active=True).select_related('plant')
        
        for line in all_lines:
            # Buscar todos os produtos ativos
            all_products = Product.objects.filter(is_active=True)
            
            products_data = []
            for product in all_products:
                products_data.append({
                    'product': product,
                    'sample': None,
                    'analyses': None,
                    'property_analyses': {},
                    'status': 'PENDENTE',
                    'sequence': None,
                    'observations': '',
                    'sample_time': None
                })
            
            if products_data:
                lines_list.append({
                    'line': line,
                    'plant': line.plant,
                    'products': products_data
                })
    
    # Estatísticas gerais
    total_samples_today = SpotSample.objects.filter(date=today).count()
    
    approved_samples = SpotSample.objects.filter(
        date=today
    ).annotate(
        has_rejected=Count('spotanalysis', filter=Q(spotanalysis__status='REJECTED'))
    ).filter(has_rejected=0).count()
    
    rejected_samples = SpotSample.objects.filter(
        date=today
    ).annotate(
        has_rejected=Count('spotanalysis', filter=Q(spotanalysis__status='REJECTED'))
    ).filter(has_rejected__gt=0).count()
    
    context = {
        'lines_data': lines_list,
        'properties': properties,
        'current_shift': current_shift,
        'current_date': today,
        'production': None,  # Não depende de cadastro de produção
        'stats': {
            'total_samples': total_samples_today,
            'approved_samples': approved_samples,
            'rejected_samples': rejected_samples,
            'approval_rate': (approved_samples / total_samples_today * 100) if total_samples_today > 0 else 0
        }
    }
    
    print(f"🔍 DEBUG: Contexto preparado - {len(lines_list)} linhas, {properties.count()} propriedades")
    
    return render(request, 'quality_control/spot_dashboard_by_line.html', context)

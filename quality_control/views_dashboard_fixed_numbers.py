"""
View corrigida para o dashboard com tratamento correto de números decimais
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Count, Q
from core.models import Shift, Plant, ProductionLine
from quality_control.models import Property, SpotSample, SpotAnalysis, Product


def parse_decimal_value(value):
    """
    Converte string com vírgula para float
    Ex: '94,00' -> 94.0
    """
    if value is None:
        return None
    
    # Se já é um número, retorna
    if isinstance(value, (int, float)):
        return float(value)
    
    # Se é string, converte vírgula para ponto
    if isinstance(value, str):
        try:
            # Remove espaços e converte vírgula para ponto
            cleaned = str(value).strip().replace(',', '.')
            return float(cleaned)
        except (ValueError, TypeError):
            return None
    
    return None


def calculate_sample_status(analyses):
    """
    Calcula o status da amostra baseado nas análises
    """
    if not analyses:
        return 'PENDENTE'
    
    has_rejected = False
    has_alert = False
    
    for analysis in analyses:
        # Converter valor para float
        value = parse_decimal_value(analysis.value)
        
        if value is None:
            continue
        
        # Verificar critérios de aprovação
        min_value = parse_decimal_value(analysis.property.min_value)
        max_value = parse_decimal_value(analysis.property.max_value)
        
        if min_value is not None and max_value is not None:
            # Verificar se está dentro dos limites
            if min_value <= value <= max_value:
                # Dentro dos limites - aprovado
                pass
            else:
                # Fora dos limites - rejeitado
                has_rejected = True
                print(f"🔍 DEBUG: {analysis.property.name} = {value} está fora dos limites {min_value}-{max_value}")
        else:
            # Sem critérios definidos - considerar aprovado
            pass
    
    if has_rejected:
        return 'REJECTED'
    elif has_alert:
        return 'ALERT'
    else:
        return 'APPROVED'


@csrf_exempt
@login_required
def spot_dashboard_by_line_view_fixed_numbers(request):
    """
    Dashboard de amostras pontuais - VERSÃO COM NÚMEROS CORRIGIDOS
    """
    print("🔍 DEBUG: Iniciando dashboard com números corrigidos")
    
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
    
    # BUSCAR TODAS AS AMOSTRAS SEM FILTRO DE DATA
    print("🔍 DEBUG: Buscando TODAS as amostras...")
    all_samples = SpotSample.objects.all().select_related(
        'product', 'production_line', 'production_line__plant', 'shift'
    ).order_by('production_line', 'product', '-sample_sequence')
    
    print(f"🔍 DEBUG: Total de amostras encontradas: {all_samples.count()}")
    
    # Organizar dados por linha de produção
    lines_data = {}
    
    for sample in all_samples:
        print(f"🔍 DEBUG: Processando amostra {sample.id} - {sample.product.name} - {sample.production_line.name}")
        
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
            print(f"🔍 DEBUG: Nova linha criada: {line.name} - {plant.name}")
        
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
            print(f"🔍 DEBUG: Novo produto adicionado: {sample.product.name}")
        
        # Buscar análises desta amostra
        analyses = SpotAnalysis.objects.filter(
            spot_sample=sample
        ).select_related('property').order_by('property__display_order')
        
        print(f"🔍 DEBUG: Amostra {sample.id} - {analyses.count()} análises encontradas")
        
        # Organizar análises por propriedade
        property_analyses = {}
        for analysis in analyses:
            property_analyses[analysis.property_id] = analysis
            
            # Debug da análise
            value = parse_decimal_value(analysis.value)
            min_val = parse_decimal_value(analysis.property.min_value)
            max_val = parse_decimal_value(analysis.property.max_value)
            
            print(f"  - {analysis.property.name}: {analysis.value} -> {value}")
            print(f"    Critérios: {analysis.property.min_value} -> {min_val} a {analysis.property.max_value} -> {max_val}")
            
            if min_val is not None and max_val is not None and value is not None:
                is_approved = min_val <= value <= max_val
                print(f"    Aprovado? {is_approved} ({min_val} <= {value} <= {max_val})")
            else:
                print(f"    Aprovado? Sem critérios ou valor inválido")
        
        # Calcular status geral da amostra usando a função corrigida
        sample_status = calculate_sample_status(analyses)
        
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
        
        print(f"🔍 DEBUG: Status calculado: {sample_status}")
    
    # Converter para lista
    lines_list = []
    for line_data in lines_data.values():
        # Converter produtos para lista
        products_list = list(line_data['products'].values())
        line_data['products'] = products_list
        lines_list.append(line_data)
        print(f"🔍 DEBUG: Linha {line_data['line'].name} - {len(products_list)} produtos")
    
    print(f"🔍 DEBUG: Total de linhas processadas: {len(lines_list)}")
    
    # Se não há dados, buscar produtos sem amostras
    if not lines_list:
        print("🔍 DEBUG: Nenhuma amostra encontrada, buscando produtos sem amostras")
        
        # Buscar todas as linhas ativas
        all_lines = ProductionLine.objects.filter(is_active=True).select_related('plant')
        print(f"🔍 DEBUG: Linhas ativas encontradas: {all_lines.count()}")
        
        for line in all_lines:
            # Buscar todos os produtos ativos
            all_products = Product.objects.filter(is_active=True)
            print(f"🔍 DEBUG: Produtos ativos encontrados: {all_products.count()}")
            
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
                print(f"🔍 DEBUG: Linha {line.name} adicionada com {len(products_data)} produtos")
    
    # Estatísticas gerais - BUSCAR TODAS AS AMOSTRAS
    total_samples = SpotSample.objects.all().count()
    print(f"🔍 DEBUG: Total de amostras para estatísticas: {total_samples}")
    
    approved_samples = SpotSample.objects.annotate(
        has_rejected=Count('spotanalysis', filter=Q(spotanalysis__status='REJECTED'))
    ).filter(has_rejected=0).count()
    
    rejected_samples = SpotSample.objects.annotate(
        has_rejected=Count('spotanalysis', filter=Q(spotanalysis__status='REJECTED'))
    ).filter(has_rejected__gt=0).count()
    
    print(f"🔍 DEBUG: Aprovadas: {approved_samples}, Rejeitadas: {rejected_samples}")
    
    context = {
        'lines_data': lines_list,
        'properties': properties,
        'current_shift': current_shift,
        'current_date': timezone.now().date(),
        'production': None,
        'stats': {
            'total_samples': total_samples,
            'approved_samples': approved_samples,
            'rejected_samples': rejected_samples,
            'approval_rate': (approved_samples / total_samples * 100) if total_samples > 0 else 0
        }
    }
    
    print(f"🔍 DEBUG: Contexto preparado - {len(lines_list)} linhas, {properties.count()} propriedades")
    print(f"🔍 DEBUG: Estatísticas - Total: {total_samples}, Aprovadas: {approved_samples}, Rejeitadas: {rejected_samples}")
    
    return render(request, 'quality_control/spot_dashboard_by_line.html', context)

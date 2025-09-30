"""
View inteligente para o dashboard - turno atual com fallback para todos os turnos de hoje
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Count, Q
from core.models import Shift, Plant, ProductionLine
from quality_control.models import Property, SpotSample, SpotAnalysis, Product
import pytz


@csrf_exempt
@login_required
def spot_dashboard_by_line_view_smart(request):
    """
    Dashboard de amostras pontuais - VERSÃO INTELIGENTE
    Prioriza turno atual, mas mostra todos os turnos de hoje se não houver dados do turno atual
    """
    print("🔍 DEBUG: Iniciando dashboard inteligente")
    
    # Obter horário correto do Brasil
    brazil_tz = pytz.timezone('America/Sao_Paulo')
    current_time_brazil = timezone.now().astimezone(brazil_tz)
    
    print(f"🔍 DEBUG: Horário UTC: {timezone.now()}")
    print(f"🔍 DEBUG: Horário Brasil: {current_time_brazil}")
    print(f"🔍 DEBUG: Hora Brasil: {current_time_brazil.hour}")
    
    # Obter turno atual baseado no horário do Brasil
    current_shift = None
    
    # Lógica para determinar o turno atual baseado no horário do Brasil
    if 7 <= current_time_brazil.hour < 19:
        current_shift = Shift.objects.filter(name='A').first()
        print("🔍 DEBUG: Turno A (7h-19h) - Horário Brasil")
    else:
        current_shift = Shift.objects.filter(name='B').first()
        print("🔍 DEBUG: Turno B (19h-7h) - Horário Brasil")
    
    if not current_shift:
        current_shift = Shift.objects.first()
        print("🔍 DEBUG: Usando primeiro turno disponível")
    
    # Garantir que temos um turno válido
    if not current_shift:
        current_shift = Shift.objects.create(
            name='A',
            start_time='07:00',
            end_time='19:00'
        )
        print("🔍 DEBUG: Criado turno padrão A")
    
    print(f"🔍 DEBUG: Turno atual: {current_shift.name}")
    
    # Obter todas as propriedades ativas
    properties = Property.objects.filter(is_active=True).order_by('display_order')
    print(f"🔍 DEBUG: Propriedades encontradas: {properties.count()}")
    
    today = timezone.now().date()
    print(f"🔍 DEBUG: Data atual: {today}")
    
    # ESTRATÉGIA INTELIGENTE: Priorizar turno atual, mas mostrar todos os turnos de hoje se necessário
    all_samples = None
    used_shift = None
    strategy_used = ""
    
    # 1. Tentar buscar amostras do turno atual
    print(f"🔍 DEBUG: Tentando buscar amostras do turno {current_shift.name}...")
    current_samples = SpotSample.objects.filter(
        date=today,
        shift=current_shift
    ).select_related(
        'product', 'production_line', 'production_line__plant', 'shift'
    ).order_by('production_line', 'product', '-sample_sequence')
    
    print(f"🔍 DEBUG: Amostras do turno atual: {current_samples.count()}")
    
    if current_samples.exists():
        all_samples = current_samples
        used_shift = current_shift
        strategy_used = f"Turno {current_shift.name} de hoje"
        print(f"🔍 DEBUG: ✅ Usando amostras do turno {current_shift.name}")
    else:
        # 2. Se não há amostras do turno atual, buscar todos os turnos de hoje
        print("🔍 DEBUG: Nenhuma amostra do turno atual, buscando todos os turnos de hoje...")
        all_today_samples = SpotSample.objects.filter(
            date=today
        ).select_related(
            'product', 'production_line', 'production_line__plant', 'shift'
        ).order_by('production_line', 'product', '-sample_sequence')
        
        print(f"🔍 DEBUG: Amostras de todos os turnos hoje: {all_today_samples.count()}")
        
        if all_today_samples.exists():
            all_samples = all_today_samples
            used_shift = None  # Múltiplos turnos
            strategy_used = "Todos os turnos de hoje"
            print("🔍 DEBUG: ✅ Usando amostras de todos os turnos de hoje")
        else:
            # 3. Se não há amostras hoje, buscar amostras recentes
            print("🔍 DEBUG: Nenhuma amostra hoje, buscando amostras recentes...")
            recent_samples = SpotSample.objects.filter(
                date__lte=today
            ).select_related(
                'product', 'production_line', 'production_line__plant', 'shift'
            ).order_by('-date', 'production_line', 'product', '-sample_sequence')[:50]  # Limitar a 50 amostras
            
            print(f"🔍 DEBUG: Amostras recentes: {recent_samples.count()}")
            
            if recent_samples.exists():
                all_samples = recent_samples
                used_shift = None  # Múltiplos turnos/datas
                strategy_used = "Amostras recentes"
                print("🔍 DEBUG: ✅ Usando amostras recentes")
            else:
                print("🔍 DEBUG: ❌ Nenhuma amostra encontrada no sistema")
                all_samples = SpotSample.objects.none()
                strategy_used = "Nenhuma amostra"
    
    print(f"🔍 DEBUG: Estratégia usada: {strategy_used}")
    print(f"🔍 DEBUG: Total de amostras a processar: {all_samples.count()}")
    
    # Organizar dados por linha de produção
    lines_data = {}
    
    for sample in all_samples:
        print(f"🔍 DEBUG: Processando amostra {sample.id} - {sample.product.name} - {sample.production_line.name} - Turno: {sample.shift.name}")
        
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
            print(f"  - {analysis.property.name}: {analysis.value} {analysis.property.unit} ({analysis.status})")
        
        # Calcular status geral da amostra baseado no status das análises
        sample_status = 'APPROVED'  # Padrão
        
        if analyses.exists():
            # Verificar se há alguma análise rejeitada
            has_rejected = analyses.filter(status='REJECTED').exists()
            has_alert = analyses.filter(status='ALERT').exists()
            
            if has_rejected:
                sample_status = 'REJECTED'
                print(f"🔍 DEBUG: Amostra rejeitada - há análises com status REJECTED")
            elif has_alert:
                sample_status = 'ALERT'
                print(f"🔍 DEBUG: Amostra em alerta - há análises com status ALERT")
            else:
                sample_status = 'APPROVED'
                print(f"🔍 DEBUG: Amostra aprovada - todas as análises estão aprovadas")
        else:
            sample_status = 'PENDENTE'
            print(f"🔍 DEBUG: Amostra pendente - sem análises")
        
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
        
        print(f"🔍 DEBUG: Status final: {sample_status}")
    
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
    
    # Estatísticas gerais - baseadas nas amostras encontradas
    total_samples = all_samples.count()
    print(f"🔍 DEBUG: Total de amostras para estatísticas: {total_samples}")
    
    # Contar amostras aprovadas (sem análises rejeitadas)
    approved_samples = all_samples.annotate(
        has_rejected=Count('spotanalysis', filter=Q(spotanalysis__status='REJECTED'))
    ).filter(has_rejected=0).count()
    
    # Contar amostras rejeitadas (com pelo menos uma análise rejeitada)
    rejected_samples = all_samples.annotate(
        has_rejected=Count('spotanalysis', filter=Q(spotanalysis__status='REJECTED'))
    ).filter(has_rejected__gt=0).count()
    
    print(f"🔍 DEBUG: Aprovadas: {approved_samples}, Rejeitadas: {rejected_samples}")
    
    # Determinar turno para exibição
    display_shift = used_shift if used_shift else current_shift
    
    context = {
        'lines_data': lines_list,
        'properties': properties,
        'current_shift': display_shift,
        'current_date': today,
        'production': None,
        'strategy_used': strategy_used,
        'stats': {
            'total_samples': total_samples,
            'approved_samples': approved_samples,
            'rejected_samples': rejected_samples,
            'approval_rate': (approved_samples / total_samples * 100) if total_samples > 0 else 0
        }
    }
    
    print(f"🔍 DEBUG: Contexto preparado - {len(lines_list)} linhas, {properties.count()} propriedades")
    print(f"🔍 DEBUG: Estatísticas - Total: {total_samples}, Aprovadas: {approved_samples}, Rejeitadas: {rejected_samples}")
    print(f"🔍 DEBUG: Turno exibido: {display_shift.name if display_shift else 'Múltiplos'}")
    print(f"🔍 DEBUG: Estratégia: {strategy_used}")
    
    return render(request, 'quality_control/spot_dashboard_by_line.html', context)

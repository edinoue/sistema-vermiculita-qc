"""
View corrigida para o dashboard por linha de produção
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Count, Q
from core.models import Shift, Plant, ProductionLine
from quality_control.models import Property, SpotSample, SpotAnalysis
from quality_control.models_production import ProductionRegistration, ProductionLineRegistration, ProductionProductRegistration


@csrf_exempt
@login_required
def spot_dashboard_by_line_view_fixed(request):
    """
    Dashboard de amostras pontuais por linha de produção - VERSÃO CORRIGIDA
    Cards para cada linha de produção cadastrada para o turno atual
    """
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
        # Se não encontrou nenhum turno, criar um padrão
        current_shift = Shift.objects.create(
            name='A',
            start_time='06:00',
            end_time='18:00'
        )
    
    # Obter produção - BUSCA MAIS FLEXÍVEL
    today = timezone.now().date()
    production = None
    
    # 1. Buscar produção ativa para o turno atual
    production = ProductionRegistration.objects.filter(
        date=today,
        shift=current_shift,
        status='ACTIVE'
    ).first()
    
    # 2. Se não encontrar, buscar qualquer produção do turno
    if not production:
        production = ProductionRegistration.objects.filter(
            date=today,
            shift=current_shift
        ).first()
    
    # 3. Se ainda não encontrar, buscar qualquer produção de hoje
    if not production:
        production = ProductionRegistration.objects.filter(
            date=today
        ).first()
    
    # 4. Se ainda não encontrar, buscar a produção mais recente
    if not production:
        production = ProductionRegistration.objects.filter(
            date__lte=today
        ).order_by('-date', '-id').first()
    
    # Obter todas as propriedades ativas
    properties = Property.objects.filter(is_active=True).order_by('display_order')
    
    # Dados para cada linha de produção
    lines_data = []
    
    if production:
        print(f"DEBUG: Usando produção {production} (status: {production.status})")
        
        # Obter linhas de produção cadastradas para esta produção
        production_lines = ProductionLineRegistration.objects.filter(
            production=production,
            is_active=True
        ).select_related('production_line__plant')
        
        # Se não encontrar linhas na produção, buscar todas as linhas ativas
        if not production_lines.exists():
            print("DEBUG: Nenhuma linha na produção, buscando todas as linhas ativas")
            all_lines = ProductionLine.objects.filter(is_active=True)
            for line in all_lines:
                # Criar registro temporário
                production_lines = [type('obj', (object,), {
                    'production_line': line,
                    'is_active': True
                })()]
                break
        
        # Para cada linha, obter dados
        for line_reg in production_lines:
            line = line_reg.production_line
            plant = line.plant
            
            # Obter produtos cadastrados para esta produção
            production_products = ProductionProductRegistration.objects.filter(
                production=production,
                is_active=True
            ).select_related('product')
            
            # Se não encontrar produtos na produção, buscar todos os produtos ativos
            if not production_products.exists():
                print(f"DEBUG: Nenhum produto na produção, buscando todos os produtos ativos")
                from quality_control.models import Product
                all_products = Product.objects.filter(is_active=True)
                production_products = [type('obj', (object,), {
                    'product': product,
                    'is_active': True
                })() for product in all_products]
            
            # Dados dos produtos para esta linha
            products_data = []
            
            for prod_reg in production_products:
                product = prod_reg.product
                
                # Buscar a amostra mais recente deste produto nesta linha
                latest_sample = SpotSample.objects.filter(
                    production_line=line,
                    product=product,
                    date=today,
                    shift=current_shift
                ).order_by('-sample_sequence', '-created_at').first()
                
                # Se não encontrar amostra do turno atual, buscar qualquer amostra
                if not latest_sample:
                    latest_sample = SpotSample.objects.filter(
                        production_line=line,
                        product=product,
                        date=today
                    ).order_by('-sample_sequence', '-created_at').first()
                
                if latest_sample:
                    # Buscar todas as análises desta amostra
                    analyses = SpotAnalysis.objects.filter(
                        spot_sample=latest_sample
                    ).select_related('property').order_by('property__display_order')
                    
                    # Organizar análises por propriedade
                    property_analyses = {}
                    for analysis in analyses:
                        property_analyses[analysis.property_id] = analysis
                    
                    # Calcular status geral da amostra
                    sample_status = 'APPROVED'
                    has_rejected = analyses.filter(status='REJECTED').exists()
                    has_alert = analyses.filter(status='ALERT').exists()
                    
                    if has_rejected:
                        sample_status = 'REJECTED'
                    elif has_alert:
                        sample_status = 'ALERT'
                    
                    products_data.append({
                        'product': product,
                        'sample': latest_sample,
                        'analyses': analyses,
                        'property_analyses': property_analyses,
                        'status': sample_status,
                        'sequence': latest_sample.sample_sequence,
                        'observations': latest_sample.observations,
                        'sample_time': latest_sample.sample_time
                    })
                else:
                    # Incluir produto mesmo sem amostra
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
            
            # Incluir a linha com seus dados
            lines_data.append({
                'line': line,
                'plant': plant,
                'products': products_data
            })
    else:
        # Se não há produção cadastrada, mostrar mensagem
        lines_data = []
        print("DEBUG: Nenhuma produção encontrada")
    
    # Estatísticas gerais
    total_samples_today = SpotSample.objects.filter(
        date=today,
        shift=current_shift
    ).count()
    
    approved_samples = SpotSample.objects.filter(
        date=today,
        shift=current_shift
    ).annotate(
        has_rejected=Count('spotanalysis', filter=Q(spotanalysis__status='REJECTED'))
    ).filter(has_rejected=0).count()
    
    rejected_samples = SpotSample.objects.filter(
        date=today,
        shift=current_shift
    ).annotate(
        has_rejected=Count('spotanalysis', filter=Q(spotanalysis__status='REJECTED'))
    ).filter(has_rejected__gt=0).count()
    
    context = {
        'lines_data': lines_data,
        'properties': properties,
        'current_shift': current_shift,
        'current_date': today,
        'production': production,
        'stats': {
            'total_samples': total_samples_today,
            'approved_samples': approved_samples,
            'rejected_samples': rejected_samples,
            'approval_rate': (approved_samples / total_samples_today * 100) if total_samples_today > 0 else 0
        }
    }
    
    return render(request, 'quality_control/spot_dashboard_by_line.html', context)

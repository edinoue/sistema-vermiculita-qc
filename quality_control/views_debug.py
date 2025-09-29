"""
Views de debug para diagnosticar problemas com sequência
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime, timedelta

from core.models import ProductionLine, Shift
from .models import Product, Property, SpotAnalysis, SpotSample, AnalysisType

@login_required
def debug_sequence_view(request):
    """View de debug para verificar a sequência"""
    
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
    
    # Obter dados
    production_lines = ProductionLine.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)
    today = timezone.now().date()
    
    debug_data = []
    
    for line in production_lines:
        line_data = {
            'line': line,
            'products': []
        }
        
        for product in products:
            # Buscar todas as amostras para este produto/linha/turno/data
            samples = SpotSample.objects.filter(
                production_line=line,
                product=product,
                date=today,
                shift=current_shift
            ).order_by('-sample_sequence', '-created_at')
            
            product_data = {
                'product': product,
                'samples': [],
                'latest_sample': None,
                'sequence_issues': []
            }
            
            for sample in samples:
                sample_info = {
                    'id': sample.id,
                    'sample_sequence': sample.sample_sequence,
                    'sample_time': sample.sample_time,
                    'created_at': sample.created_at,
                    'status': sample.status,
                    'analyses_count': sample.spotanalysis_set.count()
                }
                product_data['samples'].append(sample_info)
                
                # Verificar problemas
                if not sample.sample_sequence:
                    product_data['sequence_issues'].append(f"Amostra {sample.id} sem sequência")
            
            # Amostra mais recente
            if samples.exists():
                latest = samples.first()
                product_data['latest_sample'] = {
                    'id': latest.id,
                    'sequence': latest.sample_sequence,
                    'time': latest.sample_time,
                    'has_sequence': bool(latest.sample_sequence)
                }
            
            line_data['products'].append(product_data)
        
        debug_data.append(line_data)
    
    # Estatísticas gerais
    stats = {
        'total_samples_today': SpotSample.objects.filter(date=today).count(),
        'samples_with_sequence': SpotSample.objects.filter(date=today, sample_sequence__isnull=False).count(),
        'samples_without_sequence': SpotSample.objects.filter(date=today, sample_sequence__isnull=True).count(),
        'current_shift': current_shift,
        'today': today
    }
    
    context = {
        'debug_data': debug_data,
        'stats': stats
    }
    
    return render(request, 'quality_control/debug_sequence.html', context)

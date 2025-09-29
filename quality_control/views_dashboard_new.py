"""
Views para o novo dashboard
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Q

from .models_production import ProductionRegistration, SpotAnalysisRegistration

@login_required
def dashboard_new_view(request):
    """Novo dashboard principal do sistema"""
    
    # Estatísticas gerais
    total_productions = ProductionRegistration.objects.count()
    total_analyses = SpotAnalysisRegistration.objects.count()
    approved_analyses = SpotAnalysisRegistration.objects.filter(analysis_result='APPROVED').count()
    rejected_analyses = SpotAnalysisRegistration.objects.filter(analysis_result='REJECTED').count()
    
    # Produções recentes
    recent_productions = ProductionRegistration.objects.all().order_by('-created_at')[:5]
    
    # Análises recentes
    recent_analyses = SpotAnalysisRegistration.objects.all().order_by('-created_at')[:5]
    
    context = {
        'today': timezone.now().date(),
        'stats': {
            'total_productions': total_productions,
            'total_analyses': total_analyses,
            'approved_analyses': approved_analyses,
            'rejected_analyses': rejected_analyses,
        },
        'recent_productions': recent_productions,
        'recent_analyses': recent_analyses,
    }
    
    return render(request, 'quality_control/dashboard_new.html', context)

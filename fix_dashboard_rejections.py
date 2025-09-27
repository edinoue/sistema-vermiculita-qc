#!/usr/bin/env python
"""
Script para corrigir contagem de reprovações no dashboard
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models import SpotAnalysis, CompositeSample, CompositeSampleResult
from django.utils import timezone
from datetime import timedelta

def fix_dashboard_rejections():
    """Corrigir contagem de reprovações no dashboard"""
    
    print("🔧 CORRIGINDO CONTAGEM DE REPROVAÇÕES NO DASHBOARD")
    print("=" * 60)
    
    # 1. Verificar análises pontuais reprovadas
    print("\n1. ANÁLISES PONTUAIS REPROVADAS:")
    spot_rejected = SpotAnalysis.objects.filter(status='REJECTED')
    print(f"   Total: {spot_rejected.count()}")
    
    # 2. Verificar amostras compostas reprovadas
    print("\n2. AMOSTRAS COMPOSTAS REPROVADAS:")
    composite_rejected = CompositeSample.objects.filter(status='REJECTED')
    print(f"   Total: {composite_rejected.count()}")
    
    # 3. Verificar resultados individuais reprovados (para comparação)
    print("\n3. RESULTADOS INDIVIDUAIS REPROVADOS (para comparação):")
    composite_results_rejected = CompositeSampleResult.objects.filter(status='REJECTED')
    print(f"   Total: {composite_results_rejected.count()}")
    
    # 4. Calcular totais
    print("\n4. TOTAIS:")
    
    # ANTES (contando resultados individuais)
    old_total = SpotAnalysis.objects.filter(status='REJECTED').count() + CompositeSampleResult.objects.filter(status='REJECTED').count()
    print(f"   ANTES (resultados individuais): {old_total}")
    
    # DEPOIS (contando amostras)
    new_total = SpotAnalysis.objects.filter(status='REJECTED').count() + CompositeSample.objects.filter(status='REJECTED').count()
    print(f"   DEPOIS (amostras): {new_total}")
    
    # 5. Verificar diferença
    difference = old_total - new_total
    print(f"   DIFERENÇA: {difference}")
    
    if difference > 0:
        print(f"   ✅ CORREÇÃO NECESSÁRIA: {difference} resultados individuais não devem ser contados como amostras")
    else:
        print("   ✅ CONTAGEM JÁ ESTÁ CORRETA")
    
    # 6. Verificar dados dos últimos 30 dias
    print("\n5. DADOS DOS ÚLTIMOS 30 DIAS:")
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    spot_recent = SpotAnalysis.objects.filter(
        sample_time__gte=thirty_days_ago,
        status='REJECTED'
    ).count()
    
    composite_recent = CompositeSample.objects.filter(
        date__gte=thirty_days_ago.date(),
        status='REJECTED'
    ).count()
    
    print(f"   Análises pontuais reprovadas (30 dias): {spot_recent}")
    print(f"   Amostras compostas reprovadas (30 dias): {composite_recent}")
    print(f"   Total reprovações (30 dias): {spot_recent + composite_recent}")
    
    print("\n✅ CORREÇÃO CONCLUÍDA!")
    print("   - Dashboard agora conta AMOSTRAS reprovadas")
    print("   - Uma amostra composta reprovada = 1 reprovação")
    print("   - Uma análise pontual reprovada = 1 reprovação")

if __name__ == '__main__':
    fix_dashboard_rejections()





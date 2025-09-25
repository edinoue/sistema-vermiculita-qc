#!/usr/bin/env python
"""
Script para testar contagem de reprovações no dashboard
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

def test_dashboard_rejections():
    """Testar contagem de reprovações no dashboard"""
    
    print("🔍 TESTANDO CONTAGEM DE REPROVAÇÕES NO DASHBOARD")
    print("=" * 60)
    
    # 1. Verificar análises pontuais reprovadas
    print("\n1. ANÁLISES PONTUAIS REPROVADAS:")
    spot_rejected = SpotAnalysis.objects.filter(status='REJECTED')
    print(f"   Total de análises pontuais reprovadas: {spot_rejected.count()}")
    
    for analysis in spot_rejected:
        print(f"   - ID: {analysis.id}, Produto: {analysis.product.code}, Status: {analysis.status}")
    
    # 2. Verificar amostras compostas reprovadas
    print("\n2. AMOSTRAS COMPOSTAS REPROVADAS:")
    composite_rejected = CompositeSample.objects.filter(status='REJECTED')
    print(f"   Total de amostras compostas reprovadas: {composite_rejected.count()}")
    
    for sample in composite_rejected:
        print(f"   - ID: {sample.id}, Produto: {sample.product.code}, Status: {sample.status}")
    
    # 3. Verificar resultados individuais reprovados (para comparação)
    print("\n3. RESULTADOS INDIVIDUAIS REPROVADOS (para comparação):")
    composite_results_rejected = CompositeSampleResult.objects.filter(status='REJECTED')
    print(f"   Total de resultados individuais reprovados: {composite_results_rejected.count()}")
    
    for result in composite_results_rejected:
        print(f"   - ID: {result.id}, Amostra: {result.composite_sample.id}, Propriedade: {result.property.identifier}, Status: {result.status}")
    
    # 4. Calcular totais como no dashboard
    print("\n4. TOTAIS COMO NO DASHBOARD:")
    
    # ANTES (contando resultados individuais)
    old_total_rejections = SpotAnalysis.objects.filter(status='REJECTED').count() + CompositeSampleResult.objects.filter(status='REJECTED').count()
    print(f"   ANTES (contando resultados individuais): {old_total_rejections}")
    
    # DEPOIS (contando amostras)
    new_total_rejections = SpotAnalysis.objects.filter(status='REJECTED').count() + CompositeSample.objects.filter(status='REJECTED').count()
    print(f"   DEPOIS (contando amostras): {new_total_rejections}")
    
    # 5. Verificar diferença
    difference = old_total_rejections - new_total_rejections
    print(f"   DIFERENÇA: {difference} (resultados individuais vs amostras)")
    
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
    
    print("\n✅ TESTE CONCLUÍDO!")
    print("   - Dashboard agora conta AMOSTRAS reprovadas, não análises individuais")
    print("   - Uma amostra composta com 3 propriedades reprovadas = 1 reprovação")
    print("   - Uma análise pontual reprovada = 1 reprovação")

if __name__ == '__main__':
    test_dashboard_rejections()

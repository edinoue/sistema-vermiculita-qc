#!/usr/bin/env python
"""
Script para debugar contagem de reprovações no dashboard
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

def debug_dashboard_rejections():
    """Debugar contagem de reprovações no dashboard"""
    
    print("🔍 DEBUGANDO CONTAGEM DE REPROVAÇÕES NO DASHBOARD")
    print("=" * 60)
    
    # 1. Verificar análises pontuais
    print("\n1. ANÁLISES PONTUAIS:")
    spot_total = SpotAnalysis.objects.count()
    spot_rejected = SpotAnalysis.objects.filter(status='REJECTED').count()
    spot_approved = SpotAnalysis.objects.filter(status='APPROVED').count()
    spot_alert = SpotAnalysis.objects.filter(status='ALERT').count()
    
    print(f"   Total: {spot_total}")
    print(f"   Reprovadas: {spot_rejected}")
    print(f"   Aprovadas: {spot_approved}")
    print(f"   Alertas: {spot_alert}")
    
    # 2. Verificar amostras compostas
    print("\n2. AMOSTRAS COMPOSTAS:")
    composite_total = CompositeSample.objects.count()
    composite_rejected = CompositeSample.objects.filter(status='REJECTED').count()
    composite_approved = CompositeSample.objects.filter(status='APPROVED').count()
    composite_alert = CompositeSample.objects.filter(status='ALERT').count()
    
    print(f"   Total: {composite_total}")
    print(f"   Reprovadas: {composite_rejected}")
    print(f"   Aprovadas: {composite_approved}")
    print(f"   Alertas: {composite_alert}")
    
    # 3. Verificar resultados individuais (para comparação)
    print("\n3. RESULTADOS INDIVIDUAIS DE AMOSTRAS COMPOSTAS:")
    results_total = CompositeSampleResult.objects.count()
    results_rejected = CompositeSampleResult.objects.filter(status='REJECTED').count()
    results_approved = CompositeSampleResult.objects.filter(status='APPROVED').count()
    results_alert = CompositeSampleResult.objects.filter(status='ALERT').count()
    
    print(f"   Total: {results_total}")
    print(f"   Reprovados: {results_rejected}")
    print(f"   Aprovados: {results_approved}")
    print(f"   Alertas: {results_alert}")
    
    # 4. Calcular totais como no dashboard
    print("\n4. TOTAIS COMO NO DASHBOARD:")
    
    # ANTES (contando resultados individuais)
    old_total_rejections = spot_rejected + results_rejected
    print(f"   ANTES (resultados individuais): {old_total_rejections}")
    
    # DEPOIS (contando amostras)
    new_total_rejections = spot_rejected + composite_rejected
    print(f"   DEPOIS (amostras): {new_total_rejections}")
    
    # 5. Verificar dados dos últimos 30 dias
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
    
    # 6. Verificar dados de hoje
    print("\n6. DADOS DE HOJE:")
    today = timezone.now().date()
    
    spot_today = SpotAnalysis.objects.filter(
        sample_time__date=today,
        status='REJECTED'
    ).count()
    
    composite_today = CompositeSample.objects.filter(
        date=today,
        status='REJECTED'
    ).count()
    
    print(f"   Análises pontuais reprovadas (hoje): {spot_today}")
    print(f"   Amostras compostas reprovadas (hoje): {composite_today}")
    print(f"   Total reprovações (hoje): {spot_today + composite_today}")
    
    # 7. Listar análises reprovadas
    print("\n7. ANÁLISES REPROVADAS DETALHADAS:")
    
    print("\n   ANÁLISES PONTUAIS REPROVADAS:")
    spot_rejected_list = SpotAnalysis.objects.filter(status='REJECTED')
    for analysis in spot_rejected_list:
        print(f"   - ID: {analysis.id}, Data: {analysis.date}, Produto: {analysis.product.code}, Propriedade: {analysis.property.identifier}, Status: {analysis.status}")
    
    print("\n   AMOSTRAS COMPOSTAS REPROVADAS:")
    composite_rejected_list = CompositeSample.objects.filter(status='REJECTED')
    for sample in composite_rejected_list:
        print(f"   - ID: {sample.id}, Data: {sample.date}, Produto: {sample.product.code}, Status: {sample.status}")
    
    print("\n✅ DEBUG CONCLUÍDO!")
    
    if new_total_rejections == 0:
        print("   ⚠️  PROBLEMA: Nenhuma reprovação encontrada")
        print("   - Verifique se as amostras foram realmente reprovadas")
        print("   - Verifique se o status está sendo calculado corretamente")
    else:
        print(f"   ✅ {new_total_rejections} reprovações encontradas")

if __name__ == '__main__':
    debug_dashboard_rejections()






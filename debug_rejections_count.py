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

def debug_rejections_count():
    """Debugar contagem de reprovações"""
    
    print("🔍 DEBUGANDO CONTAGEM DE REPROVAÇÕES")
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
    print(f"   Reprovadas: {results_rejected}")
    print(f"   Aprovadas: {results_approved}")
    print(f"   Alertas: {results_alert}")
    
    # 4. Calcular totais como no dashboard
    print("\n4. CÁLCULO DO DASHBOARD:")
    
    # Método atual (contando amostras)
    total_rejections_current = spot_rejected + composite_rejected
    print(f"   Total reprovações (método atual - amostras): {total_rejections_current}")
    
    # Método antigo (contando resultados individuais)
    total_rejections_old = spot_rejected + results_rejected
    print(f"   Total reprovações (método antigo - resultados): {total_rejections_old}")
    
    # 5. Verificar dados de hoje
    print("\n5. DADOS DE HOJE:")
    today = timezone.now().date()
    
    spot_today_rejected = SpotAnalysis.objects.filter(
        sample_time__date=today,
        status='REJECTED'
    ).count()
    
    composite_today_rejected = CompositeSample.objects.filter(
        date=today,
        status='REJECTED'
    ).count()
    
    today_rejections_current = spot_today_rejected + composite_today_rejected
    print(f"   Reprovações hoje (método atual): {today_rejections_current}")
    
    # 6. Verificar se há dados de teste
    print("\n6. VERIFICANDO DADOS DE TESTE:")
    if spot_total > 0 or composite_total > 0:
        print("   ✅ Há dados no sistema")
        
        # Mostrar algumas amostras reprovadas
        print("\n   Amostras pontuais reprovadas:")
        for analysis in SpotAnalysis.objects.filter(status='REJECTED')[:5]:
            print(f"     - ID: {analysis.id}, Data: {analysis.sample_time}, Status: {analysis.status}")
        
        print("\n   Amostras compostas reprovadas:")
        for sample in CompositeSample.objects.filter(status='REJECTED')[:5]:
            print(f"     - ID: {sample.id}, Data: {sample.date}, Status: {sample.status}")
            
    else:
        print("   ❌ Não há dados no sistema")
        print("   💡 Sugestão: Criar dados de teste para verificar o dashboard")
    
    print("\n" + "="*60)
    print("CONCLUSÃO:")
    if total_rejections_current > 0:
        print(f"✅ O sistema deveria mostrar {total_rejections_current} reprovações")
        print("🔍 Verifique se a API está retornando os dados corretos")
    else:
        print("❌ Não há reprovações no sistema")
        print("💡 Crie algumas análises reprovadas para testar o dashboard")

if __name__ == "__main__":
    debug_rejections_count()

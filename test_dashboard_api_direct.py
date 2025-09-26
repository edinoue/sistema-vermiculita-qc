#!/usr/bin/env python
"""
Script para testar diretamente a API do dashboard
"""

import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')

print("🔍 TESTANDO API DO DASHBOARD DIRETAMENTE")
print("=" * 50)

try:
    import django
    django.setup()
    
    from quality_control.models import SpotAnalysis, CompositeSample
    from django.utils import timezone
    
    print("✅ Django configurado!")
    
    # 1. Verificar dados no banco
    print("\n1. VERIFICANDO DADOS NO BANCO:")
    
    spot_total = SpotAnalysis.objects.count()
    spot_rejected = SpotAnalysis.objects.filter(status='REJECTED').count()
    spot_approved = SpotAnalysis.objects.filter(status='APPROVED').count()
    
    composite_total = CompositeSample.objects.count()
    composite_rejected = CompositeSample.objects.filter(status='REJECTED').count()
    composite_approved = CompositeSample.objects.filter(status='APPROVED').count()
    
    print(f"   Análises pontuais: {spot_total} (Reprovadas: {spot_rejected}, Aprovadas: {spot_approved})")
    print(f"   Amostras compostas: {composite_total} (Reprovadas: {composite_rejected}, Aprovadas: {composite_approved})")
    
    # 2. Simular a lógica da API
    print("\n2. SIMULANDO LÓGICA DA API:")
    
    total_rejections = spot_rejected + composite_rejected
    total_approved = spot_approved + composite_approved
    
    print(f"   Total reprovações: {total_rejections}")
    print(f"   Total aprovadas: {total_approved}")
    
    # 3. Verificar dados de hoje
    print("\n3. VERIFICANDO DADOS DE HOJE:")
    today = timezone.now().date()
    
    spot_today_rejected = SpotAnalysis.objects.filter(
        sample_time__date=today,
        status='REJECTED'
    ).count()
    
    composite_today_rejected = CompositeSample.objects.filter(
        date=today,
        status='REJECTED'
    ).count()
    
    today_rejections = spot_today_rejected + composite_today_rejected
    print(f"   Reprovações hoje: {today_rejections}")
    
    # 4. Mostrar algumas análises reprovadas
    print("\n4. ANÁLISES REPROVADAS:")
    rejected_analyses = SpotAnalysis.objects.filter(status='REJECTED')[:3]
    for analysis in rejected_analyses:
        print(f"   - ID: {analysis.id}, Status: {analysis.status}, Data: {analysis.sample_time}")
    
    # 5. Resultado
    print("\n" + "="*50)
    print("RESULTADO:")
    
    if total_rejections > 0:
        print(f"✅ Há {total_rejections} reprovações no banco de dados")
        print("🔍 O problema pode estar no frontend (JavaScript) ou na chamada da API")
        print("\n💡 PRÓXIMOS PASSOS:")
        print("1. Abra o navegador e vá para o dashboard")
        print("2. Abra o console do navegador (F12)")
        print("3. Verifique se há erros na chamada da API")
        print("4. Verifique se a API está retornando os dados corretos")
    else:
        print("❌ Não há reprovações no banco de dados")
        print("💡 Execute o script fix_rejections_final.py primeiro")
    
except Exception as e:
    print(f"Erro: {e}")
    import traceback
    traceback.print_exc()

print("=" * 50)


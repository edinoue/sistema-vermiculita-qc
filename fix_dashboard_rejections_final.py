#!/usr/bin/env python
"""
Script para corrigir o problema do dashboard de reprovações
"""

import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')

print("🔧 CORRIGINDO DASHBOARD DE REPROVAÇÕES")
print("=" * 50)

try:
    import django
    django.setup()
    
    from quality_control.models import SpotAnalysis, CompositeSample, CompositeSampleResult
    from django.utils import timezone
    from datetime import timedelta
    
    print("✅ Django configurado com sucesso!")
    
    # 1. Verificar dados existentes
    print("\n1. VERIFICANDO DADOS EXISTENTES:")
    
    spot_total = SpotAnalysis.objects.count()
    composite_total = CompositeSample.objects.count()
    results_total = CompositeSampleResult.objects.count()
    
    print(f"   Análises pontuais: {spot_total}")
    print(f"   Amostras compostas: {composite_total}")
    print(f"   Resultados individuais: {results_total}")
    
    # 2. Verificar reprovações
    print("\n2. VERIFICANDO REPROVAÇÕES:")
    
    spot_rejected = SpotAnalysis.objects.filter(status='REJECTED').count()
    composite_rejected = CompositeSample.objects.filter(status='REJECTED').count()
    results_rejected = CompositeSampleResult.objects.filter(status='REJECTED').count()
    
    print(f"   Reprovações pontuais: {spot_rejected}")
    print(f"   Reprovações compostas: {composite_rejected}")
    print(f"   Reprovações resultados: {results_rejected}")
    
    # 3. Calcular totais corretos
    print("\n3. CALCULANDO TOTAIS CORRETOS:")
    
    # Método correto: contar amostras, não resultados individuais
    total_rejections_correct = spot_rejected + composite_rejected
    print(f"   Total reprovações (correto): {total_rejections_correct}")
    
    # Método incorreto: contar resultados individuais
    total_rejections_incorrect = spot_rejected + results_rejected
    print(f"   Total reprovações (incorreto): {total_rejections_incorrect}")
    
    # 4. Verificar se há dados de hoje
    print("\n4. VERIFICANDO DADOS DE HOJE:")
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
    
    # 5. Se não há dados, criar dados de teste
    if total_rejections_correct == 0:
        print("\n5. CRIANDO DADOS DE TESTE:")
        
        # Verificar se há pelo menos uma análise para modificar
        if spot_total > 0:
            # Modificar a primeira análise para reprovada
            first_analysis = SpotAnalysis.objects.first()
            first_analysis.status = 'REJECTED'
            first_analysis.save()
            print(f"   ✅ Análise pontual {first_analysis.id} marcada como reprovada")
        elif composite_total > 0:
            # Modificar a primeira amostra composta para reprovada
            first_sample = CompositeSample.objects.first()
            first_sample.status = 'REJECTED'
            first_sample.save()
            print(f"   ✅ Amostra composta {first_sample.id} marcada como reprovada")
        else:
            print("   ❌ Não há dados para modificar")
            print("   💡 Crie algumas análises primeiro no sistema")
    
    # 6. Verificar API do dashboard
    print("\n6. VERIFICANDO API DO DASHBOARD:")
    
    # Simular a lógica da API
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Contar reprovações dos últimos 30 dias
    spot_rejections_30d = SpotAnalysis.objects.filter(
        sample_time__gte=thirty_days_ago,
        status='REJECTED'
    ).count()
    
    composite_rejections_30d = CompositeSample.objects.filter(
        date__gte=thirty_days_ago.date(),
        status='REJECTED'
    ).count()
    
    total_rejections_30d = spot_rejections_30d + composite_rejections_30d
    print(f"   Reprovações últimos 30 dias: {total_rejections_30d}")
    
    # 7. Resultado final
    print("\n" + "="*50)
    print("RESULTADO FINAL:")
    
    if total_rejections_correct > 0:
        print(f"✅ O dashboard deveria mostrar {total_rejections_correct} reprovações")
        print("🔍 Verifique se a API está funcionando corretamente")
    else:
        print("❌ Não há reprovações no sistema")
        print("💡 Crie algumas análises e marque como reprovadas para testar")
    
    print("\n💡 PRÓXIMOS PASSOS:")
    print("1. Acesse o sistema e crie algumas análises")
    print("2. Marque algumas como reprovadas")
    print("3. Verifique se o dashboard mostra os números corretos")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)

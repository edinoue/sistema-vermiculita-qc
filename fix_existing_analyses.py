#!/usr/bin/env python
"""
Script para modificar análises existentes para criar reprovações
"""

import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')

print("🔧 MODIFICANDO ANÁLISES EXISTENTES PARA CRIAR REPROVAÇÕES")
print("=" * 60)

try:
    import django
    django.setup()
    
    from quality_control.models import SpotAnalysis, CompositeSample
    from django.contrib.auth.models import User
    
    print("✅ Django configurado com sucesso!")
    
    # 1. Verificar dados existentes
    print("\n1. VERIFICANDO DADOS EXISTENTES:")
    
    spot_total = SpotAnalysis.objects.count()
    composite_total = CompositeSample.objects.count()
    
    print(f"   Análises pontuais: {spot_total}")
    print(f"   Amostras compostas: {composite_total}")
    
    # 2. Verificar reprovações atuais
    spot_rejected = SpotAnalysis.objects.filter(status='REJECTED').count()
    composite_rejected = CompositeSample.objects.filter(status='REJECTED').count()
    
    print(f"   Reprovações pontuais atuais: {spot_rejected}")
    print(f"   Reprovações compostas atuais: {composite_rejected}")
    
    # 3. Modificar algumas análises pontuais para reprovadas
    if spot_total > 0:
        print("\n2. MODIFICANDO ANÁLISES PONTUAIS:")
        
        # Pegar algumas análises aprovadas e modificar para reprovadas
        approved_analyses = SpotAnalysis.objects.filter(status='APPROVED')[:3]
        
        for i, analysis in enumerate(approved_analyses):
            # Modificar o valor para um valor que cause reprovação
            analysis.value = 5.0  # Valor baixo para causar reprovação
            analysis.status = 'REJECTED'  # Forçar status reprovado
            analysis.save()
            print(f"   ✅ Análise {analysis.id} modificada para reprovada (valor: {analysis.value})")
    
    # 4. Modificar algumas amostras compostas para reprovadas
    if composite_total > 0:
        print("\n3. MODIFICANDO AMOSTRAS COMPOSTAS:")
        
        # Pegar algumas amostras aprovadas e modificar para reprovadas
        approved_samples = CompositeSample.objects.filter(status='APPROVED')[:2]
        
        for sample in approved_samples:
            sample.status = 'REJECTED'
            sample.save()
            print(f"   ✅ Amostra composta {sample.id} modificada para reprovada")
    
    # 5. Verificar totais finais
    print("\n4. VERIFICANDO TOTAIS FINAIS:")
    
    spot_rejected_final = SpotAnalysis.objects.filter(status='REJECTED').count()
    composite_rejected_final = CompositeSample.objects.filter(status='REJECTED').count()
    total_rejections = spot_rejected_final + composite_rejected_final
    
    print(f"   Reprovações pontuais: {spot_rejected_final}")
    print(f"   Reprovações compostas: {composite_rejected_final}")
    print(f"   Total reprovações: {total_rejections}")
    
    # 6. Verificar dados de hoje
    print("\n5. VERIFICANDO DADOS DE HOJE:")
    from django.utils import timezone
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
    
    # 7. Resultado final
    print("\n" + "="*60)
    print("RESULTADO FINAL:")
    
    if total_rejections > 0:
        print(f"✅ Dados modificados com sucesso!")
        print(f"✅ O dashboard agora deveria mostrar {total_rejections} reprovações")
        print(f"✅ Reprovações de hoje: {today_rejections}")
        print("\n💡 PRÓXIMOS PASSOS:")
        print("1. Acesse o sistema no navegador")
        print("2. Vá para o dashboard")
        print("3. Verifique se o número de reprovações está sendo exibido")
        print("4. Se ainda não funcionar, verifique o console do navegador para erros")
    else:
        print("❌ Não foi possível criar reprovações")
        print("💡 Crie algumas análises primeiro no sistema")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
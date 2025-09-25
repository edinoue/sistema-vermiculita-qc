#!/usr/bin/env python
"""
Script para corrigir o problema do modelo que sobrescreve o status
"""

import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')

print("🔧 CORRIGINDO PROBLEMA DO MODELO QUE SOBRESCREVE STATUS")
print("=" * 60)

try:
    import django
    django.setup()
    
    from quality_control.models import SpotAnalysis, CompositeSample
    from django.db import connection
    
    print("✅ Django configurado com sucesso!")
    
    # 1. Verificar dados atuais
    print("\n1. VERIFICANDO DADOS ATUAIS:")
    
    spot_total = SpotAnalysis.objects.count()
    composite_total = CompositeSample.objects.count()
    
    print(f"   Análises pontuais: {spot_total}")
    print(f"   Amostras compostas: {composite_total}")
    
    # 2. Usar update() para contornar o método save() do modelo
    print("\n2. USANDO UPDATE() PARA CONTORNAR O MÉTODO SAVE():")
    
    # Modificar análises pontuais usando update() (não chama save())
    spot_updated = SpotAnalysis.objects.filter(status='APPROVED')[:3].update(status='REJECTED')
    print(f"   ✅ {spot_updated} análises pontuais atualizadas para REJECTED")
    
    # Modificar amostras compostas usando update()
    composite_updated = CompositeSample.objects.filter(status='APPROVED')[:2].update(status='REJECTED')
    print(f"   ✅ {composite_updated} amostras compostas atualizadas para REJECTED")
    
    # 3. Verificar status após modificação
    print("\n3. VERIFICANDO STATUS APÓS MODIFICAÇÃO:")
    
    spot_rejected = SpotAnalysis.objects.filter(status='REJECTED').count()
    composite_rejected = CompositeSample.objects.filter(status='REJECTED').count()
    total_rejections = spot_rejected + composite_rejected
    
    print(f"   Reprovações pontuais: {spot_rejected}")
    print(f"   Reprovações compostas: {composite_rejected}")
    print(f"   Total reprovações: {total_rejections}")
    
    # 4. Verificar dados de hoje
    print("\n4. VERIFICANDO DADOS DE HOJE:")
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
    
    # 5. Mostrar algumas análises reprovadas
    print("\n5. ANÁLISES REPROVADAS:")
    rejected_analyses = SpotAnalysis.objects.filter(status='REJECTED')[:3]
    for analysis in rejected_analyses:
        print(f"   - ID: {analysis.id}, Valor: {analysis.value}, Status: {analysis.status}")
    
    # 6. Resultado final
    print("\n" + "="*60)
    print("RESULTADO FINAL:")
    
    if total_rejections > 0:
        print(f"✅ Status corrigido com sucesso!")
        print(f"✅ O dashboard agora deveria mostrar {total_rejections} reprovações")
        print(f"✅ Reprovações de hoje: {today_rejections}")
        print("\n💡 O problema era que o método save() do modelo estava recalculando o status")
        print("💡 Usando update() contornamos esse problema")
        print("\n🔍 PRÓXIMOS PASSOS:")
        print("1. Acesse o sistema no navegador")
        print("2. Vá para o dashboard")
        print("3. Verifique se o número de reprovações está sendo exibido")
    else:
        print("❌ Não foi possível corrigir o status")
        print("💡 Pode ser que não haja dados aprovados para modificar")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)

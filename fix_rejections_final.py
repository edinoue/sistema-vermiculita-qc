#!/usr/bin/env python
"""
Script final para corrigir reprovações usando o novo método
"""

import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')

print("🔧 CORRIGINDO REPROVAÇÕES - VERSÃO FINAL")
print("=" * 50)

try:
    import django
    django.setup()
    
    from quality_control.models import SpotAnalysis, CompositeSample
    
    print("✅ Django configurado!")
    
    # Verificar dados
    spot_total = SpotAnalysis.objects.count()
    composite_total = CompositeSample.objects.count()
    
    print(f"Análises pontuais: {spot_total}")
    print(f"Amostras compostas: {composite_total}")
    
    # Usar o novo método set_status_manually
    print("\nModificando análises pontuais...")
    analyses = SpotAnalysis.objects.filter(status='APPROVED')[:3]
    for analysis in analyses:
        analysis.set_status_manually('REJECTED')
        analysis.save()
        print(f"  ✅ Análise {analysis.id} -> REJECTED")
    
    print("\nModificando amostras compostas...")
    samples = CompositeSample.objects.filter(status='APPROVED')[:2]
    for sample in samples:
        sample.status = 'REJECTED'
        sample.save()
        print(f"  ✅ Amostra {sample.id} -> REJECTED")
    
    # Verificar resultado
    spot_rejected = SpotAnalysis.objects.filter(status='REJECTED').count()
    composite_rejected = CompositeSample.objects.filter(status='REJECTED').count()
    
    print(f"\nTotal reprovações: {spot_rejected + composite_rejected}")
    
    if spot_rejected + composite_rejected > 0:
        print("✅ SUCESSO! Dashboard deveria mostrar reprovações agora.")
    else:
        print("❌ Ainda não há reprovações")
    
except Exception as e:
    print(f"Erro: {e}")
    import traceback
    traceback.print_exc()

print("=" * 50)

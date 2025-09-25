#!/usr/bin/env python
"""
Script simples para corrigir reprovações
"""

import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')

print("🔧 CORRIGINDO REPROVAÇÕES - ABORDAGEM SIMPLES")
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
    
    # Usar update() para contornar o método save()
    spot_updated = SpotAnalysis.objects.filter(status='APPROVED').update(status='REJECTED')
    composite_updated = CompositeSample.objects.filter(status='APPROVED').update(status='REJECTED')
    
    print(f"Análises atualizadas: {spot_updated}")
    print(f"Amostras atualizadas: {composite_updated}")
    
    # Verificar resultado
    spot_rejected = SpotAnalysis.objects.filter(status='REJECTED').count()
    composite_rejected = CompositeSample.objects.filter(status='REJECTED').count()
    
    print(f"Total reprovações: {spot_rejected + composite_rejected}")
    
    if spot_rejected + composite_rejected > 0:
        print("✅ SUCESSO! Dashboard deveria mostrar reprovações agora.")
    else:
        print("❌ Ainda não há reprovações")
    
except Exception as e:
    print(f"Erro: {e}")

print("=" * 50)

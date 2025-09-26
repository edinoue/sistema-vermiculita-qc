#!/usr/bin/env python
"""
Teste rápido do dashboard
"""

import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')

print("🔍 TESTE RÁPIDO DO DASHBOARD")
print("=" * 40)

try:
    import django
    django.setup()
    
    from quality_control.models import SpotAnalysis, CompositeSample
    
    # Contar reprovações
    spot_rejected = SpotAnalysis.objects.filter(status='REJECTED').count()
    composite_rejected = CompositeSample.objects.filter(status='REJECTED').count()
    total = spot_rejected + composite_rejected
    
    print(f"Reprovações pontuais: {spot_rejected}")
    print(f"Reprovações compostas: {composite_rejected}")
    print(f"Total: {total}")
    
    if total > 0:
        print("✅ Há reprovações no banco!")
        print("🔍 Problema pode estar na API ou frontend")
        print("\n💡 TESTE MANUAL:")
        print("1. Acesse: http://localhost:8000/qc/dashboard-data/")
        print("2. Verifique se retorna JSON com total_rejections > 0")
        print("3. Se retornar 0, problema na API")
        print("4. Se retornar > 0, problema no frontend")
    else:
        print("❌ Não há reprovações no banco")
        print("💡 Execute: python fix_rejections_final.py")
    
except Exception as e:
    print(f"Erro: {e}")

print("=" * 40)


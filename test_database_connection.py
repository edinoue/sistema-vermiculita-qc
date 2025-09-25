#!/usr/bin/env python
"""
Script para testar conexão com banco de dados
"""

import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')

print("🔍 TESTANDO CONEXÃO COM BANCO DE DADOS")
print("=" * 50)

try:
    import django
    django.setup()
    
    from quality_control.models import SpotAnalysis, CompositeSample
    from django.db import connection
    
    print("✅ Django configurado com sucesso!")
    
    # Verificar conexão
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("✅ Conexão com banco OK")
    
    # Contar registros
    spot_count = SpotAnalysis.objects.count()
    composite_count = CompositeSample.objects.count()
    
    print(f"📊 Análises pontuais: {spot_count}")
    print(f"📊 Amostras compostas: {composite_count}")
    
    # Verificar reprovações
    spot_rejected = SpotAnalysis.objects.filter(status='REJECTED').count()
    composite_rejected = CompositeSample.objects.filter(status='REJECTED').count()
    
    print(f"❌ Reprovações pontuais: {spot_rejected}")
    print(f"❌ Reprovações compostas: {composite_rejected}")
    print(f"❌ Total reprovações: {spot_rejected + composite_rejected}")
    
    if spot_count > 0 or composite_count > 0:
        print("\n📋 Últimas análises:")
        for analysis in SpotAnalysis.objects.all()[:3]:
            print(f"  - ID: {analysis.id}, Status: {analysis.status}, Data: {analysis.sample_time}")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)

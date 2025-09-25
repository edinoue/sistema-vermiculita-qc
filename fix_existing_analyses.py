#!/usr/bin/env python
"""
Script para corrigir análises existentes
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models import Product, Property, Specification, SpotAnalysis, CompositeSampleResult
from decimal import Decimal

def fix_existing_analyses():
    """Corrigir análises existentes"""
    
    print("🔧 CORRIGINDO ANÁLISES EXISTENTES")
    print("=" * 50)
    
    # 1. Corrigir análises pontuais
    print("\n1. CORRIGINDO ANÁLISES PONTUAIS:")
    spot_analyses = SpotAnalysis.objects.all()
    print(f"   Total de análises pontuais: {spot_analyses.count()}")
    
    corrected_count = 0
    for analysis in spot_analyses:
        old_status = analysis.status
        analysis.save()  # Isso vai recalcular o status
        new_status = analysis.status
        
        if old_status != new_status:
            print(f"   🔄 {analysis.property.identifier}: {old_status} → {new_status}")
            corrected_count += 1
    
    print(f"   ✅ {corrected_count} análises pontuais corrigidas")
    
    # 2. Corrigir resultados de amostras compostas
    print("\n2. CORRIGINDO RESULTADOS DE AMOSTRAS COMPOSTAS:")
    composite_results = CompositeSampleResult.objects.all()
    print(f"   Total de resultados de amostras compostas: {composite_results.count()}")
    
    corrected_count = 0
    for result in composite_results:
        old_status = result.status
        result.save()  # Isso vai recalcular o status
        new_status = result.status
        
        if old_status != new_status:
            print(f"   🔄 {result.property.identifier}: {old_status} → {new_status}")
            corrected_count += 1
    
    print(f"   ✅ {corrected_count} resultados de amostras compostas corrigidos")
    
    # 3. Verificar especificações
    print("\n3. VERIFICANDO ESPECIFICAÇÕES:")
    specifications = Specification.objects.filter(is_active=True)
    print(f"   Total de especificações ativas: {specifications.count()}")
    
    for spec in specifications:
        print(f"   - {spec.product.code} - {spec.property.identifier}: LSL={spec.lsl}, USL={spec.usl}")

if __name__ == '__main__':
    fix_existing_analyses()

#!/usr/bin/env python
"""
Debug final final final de amostras compostas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models import (
    AnalysisType, Property, AnalysisTypeProperty,
    CompositeSample, CompositeSampleResult
)

def debug_final_final_final():
    """Debug final final final"""
    print("=== Debug Final Final Final Amostras Compostas ===")
    
    # 1. Verificar tipos
    print("\n1. Tipos de análise:")
    for at in AnalysisType.objects.all():
        print(f"  - {at.code}: {at.name}")
    
    # 2. Verificar propriedades
    print("\n2. Propriedades ativas:")
    for prop in Property.objects.filter(is_active=True):
        print(f"  - {prop.identifier}: {prop.name}")
    
    # 3. Verificar configuração
    print("\n3. Configuração:")
    try:
        composta_type = AnalysisType.objects.get(code='COMPOSTA')
        atp_count = AnalysisTypeProperty.objects.filter(analysis_type=composta_type).count()
        print(f"  Propriedades para COMPOSTA: {atp_count}")
    except AnalysisType.DoesNotExist:
        print("  ❌ Tipo COMPOSTA não encontrado!")
    
    # 4. Verificar amostras
    print("\n4. Amostras:")
    samples = CompositeSample.objects.all()
    print(f"  Total: {samples.count()}")
    
    for sample in samples:
        results = CompositeSampleResult.objects.filter(composite_sample=sample)
        print(f"  Amostra {sample.id}: {results.count()} resultados")
        for result in results:
            print(f"    - {result.property.identifier}: {result.value}")

if __name__ == '__main__':
    debug_final_final_final()






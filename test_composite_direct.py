#!/usr/bin/env python
"""
Teste direto de amostras compostas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models import CompositeSample, CompositeSampleResult

def test_direct():
    """Teste direto"""
    print("=== Teste Direto de Amostras Compostas ===")
    
    # Verificar amostras
    samples = CompositeSample.objects.all()
    print(f"Total: {samples.count()}")
    
    for sample in samples:
        results = CompositeSampleResult.objects.filter(composite_sample=sample)
        print(f"Amostra {sample.id}: {results.count()} resultados")
        
        for result in results:
            print(f"  {result.property.identifier}: {result.value}")

if __name__ == '__main__':
    test_direct()





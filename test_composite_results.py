#!/usr/bin/env python
"""
Testar resultados de amostras compostas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models import CompositeSample, CompositeSampleResult

def test_results():
    """Testar resultados"""
    print("=== Teste de Resultados de Amostras Compostas ===")
    
    # Verificar amostras
    samples = CompositeSample.objects.all()
    print(f"Total de amostras: {samples.count()}")
    
    for sample in samples:
        print(f"\nAmostra {sample.id}:")
        print(f"  Data: {sample.date}")
        print(f"  Produto: {sample.product.name}")
        print(f"  Status: {sample.status}")
        
        # Verificar resultados
        results = CompositeSampleResult.objects.filter(composite_sample=sample)
        print(f"  Resultados: {results.count()}")
        
        if results.count() > 0:
            for result in results:
                print(f"    - {result.property.identifier}: {result.value} {result.property.unit}")
        else:
            print("    ❌ Nenhum resultado encontrado!")
    
    print("\n=== Teste concluído ===")

if __name__ == '__main__':
    test_results()


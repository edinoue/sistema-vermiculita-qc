#!/usr/bin/env python
"""
Corrigir problemas com resultados de amostras compostas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models import AnalysisType, Property, AnalysisTypeProperty, CompositeSample, CompositeSampleResult

def fix_composite_results():
    """Corrigir problemas com resultados"""
    print("=== Corrigindo Problemas com Amostras Compostas ===")
    
    # 1. Criar tipo COMPOSTA se não existir
    composta_type, created = AnalysisType.objects.get_or_create(
        code='COMPOSTA',
        defaults={
            'name': 'Análise Composta',
            'description': 'Análises que representam 12 horas de produção',
            'frequency_per_shift': 1,
            'is_active': True
        }
    )
    print(f"Tipo COMPOSTA: {'criado' if created else 'já existe'}")
    
    # 2. Configurar propriedades para COMPOSTA
    properties = Property.objects.filter(is_active=True)
    print(f"Propriedades ativas: {properties.count()}")
    
    for prop in properties:
        atp, created = AnalysisTypeProperty.objects.get_or_create(
            analysis_type=composta_type,
            property=prop,
            defaults={
                'is_required': False,
                'display_order': prop.display_order,
                'is_active': True
            }
        )
        print(f"  {prop.identifier}: {'configurado' if created else 'já configurado'}")
    
    # 3. Verificar amostras existentes
    print("\n=== Verificando Amostras Existentes ===")
    samples = CompositeSample.objects.all()
    print(f"Total de amostras: {samples.count()}")
    
    for sample in samples:
        results = CompositeSampleResult.objects.filter(composite_sample=sample)
        print(f"Amostra {sample.id}: {results.count()} resultados")
        
        for result in results:
            print(f"  - {result.property.identifier}: {result.value} {result.property.unit}")
    
    print("\n=== Correção concluída ===")

if __name__ == '__main__':
    fix_composite_results()





